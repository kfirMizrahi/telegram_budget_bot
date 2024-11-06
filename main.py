import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler, Application, MessageHandler, filters, ContextTypes
from gspread_formatting import *



# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = 'YOUR_GOOGLE_CREDENTIALS_JSON'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
client = gspread.authorize(credentials)
spreadsheet = client.open("YOUR_GOOGLE_SPREADSHEET_NAME")

# Conversation states
COMMAND_SELECTION, INCOME_NAME, INCOME_AMOUNT, INCOME_TYPE, OUTCOME_NAME, OUTCOME_AMOUNT, OUTCOME_TYPE = range(7)

INCOME_TYPES = ["אחר", "משכורת", "מתנה", "החזר"] #add more type as you want
OUTCOME_TYPES = ["רכב", "אוכל", "תרומה", "אחר", "החזרים"] #add more type as you want

income_markup = ReplyKeyboardMarkup([[income] for income in INCOME_TYPES], one_time_keyboard=True)
outcome_markup = ReplyKeyboardMarkup([[outcome] for outcome in OUTCOME_TYPES], one_time_keyboard=True)
command_markup = ReplyKeyboardMarkup([["הכנסה", "הוצאה"]], one_time_keyboard=True)


# Helper functions for Google Sheets
def get_monthly_sheet():
    current_month = datetime.now().strftime("%m-%Y")
    try:
        sheet = spreadsheet.worksheet(current_month)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=current_month, rows="1000", cols="12")

        # Set up headers and initial settings
        sheet.update("A1", [["הכנסות"]])
        sheet.merge_cells("A1:D1")
        sheet.update("E1", [["הוצאות"]])
        sheet.merge_cells("E1:H1")
        sheet.update("A2:D2", [["תאריך", "שם", "סכום", "סוג"]])
        sheet.update("E2:H2", [["תאריך", "שם", "סכום", "סוג"]])
        sheet.update("I1", [["הכנסות"]])
        sheet.update("I2", [["=SUM(C3:C)"]], raw=False)
        sheet.update("J1", [["הוצאות"]])
        sheet.update("J2", [["=SUM(G3:G)"]], raw=False)
        sheet.update("K1", [["סה\"כ"]])
        sheet.update("K2", [["=I2-J2"]], raw=False)

        # Set formatting rules for final balance
        rule_positive = ConditionalFormatRule(
            ranges=[GridRange.from_a1_range("K2", sheet)],
            booleanRule=BooleanRule(condition=BooleanCondition("NUMBER_GREATER", ["0"]),
                                    format=CellFormat(backgroundColor=Color(0.0, 1.0, 0.0)))
        )
        rule_negative = ConditionalFormatRule(
            ranges=[GridRange.from_a1_range("K2", sheet)],
            booleanRule=BooleanRule(condition=BooleanCondition("NUMBER_LESS", ["0"]),
                                    format=CellFormat(backgroundColor=Color(1.0, 0.0, 0.0)))
        )
        rules = get_conditional_format_rules(sheet)
        rules.append(rule_negative)
        rules.append(rule_positive)
        rules.save()

        sheet_properties = {"sheetId": sheet.id, "rightToLeft": True}
        spreadsheet.batch_update(
            {"requests": [{"updateSheetProperties": {"properties": sheet_properties, "fields": "rightToLeft"}}]})

        fmt_bold = CellFormat(textFormat=TextFormat(bold=True))
        format_cell_range(sheet, "A1", fmt_bold)
        format_cell_range(sheet, "E1", fmt_bold)
        format_cell_range(sheet, "I1", fmt_bold)
        format_cell_range(sheet, "J1", fmt_bold)
        format_cell_range(sheet, "K1", fmt_bold)

        center_format = CellFormat(horizontalAlignment="CENTER", verticalAlignment="MIDDLE")
        format_cell_range(sheet, "A1:K1000", center_format)

        sheet.update("L1", [["3"]])  # Initial row for income
        sheet.update("L2", [["3"]])

    return sheet


def get_next_row(sheet, cell):
    return int(sheet.acell(cell).value)


def update_row_counter(sheet, cell, row):
    sheet.update(cell, [[str(row)]])


# Command selection
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("בחר פעולה: הכנסה או הוצאה", reply_markup=command_markup)
    return COMMAND_SELECTION


async def handle_command_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_command = update.message.text
    if selected_command == "הכנסה":
        await update.message.reply_text("נא להזין את שם ההכנסה.")
        return INCOME_NAME
    elif selected_command == "הוצאה":
        await update.message.reply_text("נא להזין את שם ההוצאה.")
        return OUTCOME_NAME
    else:
        await update.message.reply_text("בחירה לא חוקית, נסה שוב.", reply_markup=command_markup)
        return COMMAND_SELECTION


# Income entry process
async def income_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['income_name'] = update.message.text
    await update.message.reply_text("נא להזין את סכום ההכנסה.")
    return INCOME_AMOUNT


async def income_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['income_amount'] = float(update.message.text)
        await update.message.reply_text("נא לבחור את סוג ההכנסה.", reply_markup=income_markup)
        return INCOME_TYPE
    except ValueError:
        await update.message.reply_text("סכום לא חוקי. נא להזין ערך מספרי.")
        return INCOME_AMOUNT


async def income_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income_name = context.user_data['income_name']
    income_amount = context.user_data['income_amount']
    income_type = update.message.text
    date = datetime.now().strftime("%d-%m-%Y")

    sheet = get_monthly_sheet()
    income_row = get_next_row(sheet, "L1")
    sheet.update(f"A{income_row}:D{income_row}", [[date, income_name, income_amount, income_type]])
    update_row_counter(sheet, "L1", income_row + 1)

    await update.message.reply_text(f"הכנסה של {income_amount} ({income_type}) נרשמה בהצלחה.")
    return ConversationHandler.END


# Outcome entry process
async def outcome_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['outcome_name'] = update.message.text
    await update.message.reply_text("נא להזין את סכום ההוצאה.")
    return OUTCOME_AMOUNT


async def outcome_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['outcome_amount'] = float(update.message.text)
        await update.message.reply_text("נא לבחור את סוג ההוצאה.", reply_markup=outcome_markup)
        return OUTCOME_TYPE
    except ValueError:
        await update.message.reply_text("סכום לא חוקי. נא להזין ערך מספרי.")
        return OUTCOME_AMOUNT


async def outcome_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    outcome_name = context.user_data['outcome_name']
    outcome_amount = context.user_data['outcome_amount']
    outcome_type = update.message.text
    date = datetime.now().strftime("%d-%m-%Y")

    sheet = get_monthly_sheet()
    outcome_row = get_next_row(sheet, "L2")
    sheet.update(f"E{outcome_row}:H{outcome_row}", [[date, outcome_name, outcome_amount, outcome_type]])
    update_row_counter(sheet, "L2", outcome_row + 1)

    await update.message.reply_text(f"הוצאה של {outcome_amount} ({outcome_type}) נרשמה בהצלחה.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("רישום בוטל.")
    return ConversationHandler.END


def main():
    TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COMMAND_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_command_selection)],
            INCOME_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, income_name)],
            INCOME_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, income_amount)],
            INCOME_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, income_type)],
            OUTCOME_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, outcome_name)],
            OUTCOME_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, outcome_amount)],
            OUTCOME_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, outcome_type)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conversation_handler)

    app.run_polling()


if __name__ == '__main__':
    main()
