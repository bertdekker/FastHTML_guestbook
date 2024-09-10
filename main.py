import os
from datetime import datetime
import pytz
from fasthtml.common import *
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 50
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %p CET"

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app, rt = fast_app(
  hdrs=(Link(rel="icon", type="assets/x-icon", href="/assets/favicon.png"),),
)

def get_cet_time():
  cet_tz = pytz.timezone("CET")
  return datetime.now(cet_tz)

def add_message(name, message):
  timestamp = get_cet_time().strftime(TIMESTAMP_FORMAT)
  supabase.table("guestbook").insert(
    {"name": name,
     "message": message,
     "timestamp": timestamp}
     ).execute()

def get_messages():
  response = supabase.table("guestbook").select("*").order("id", desc=True).execute()
  return response.data

def render_message(entry):
    return (
      Article(
        Header(f"Naam: {entry['name']}"),
        P(entry["message"]),
        Footer(Small(Em(f"Gepost op: {entry['timestamp']}"))),
      ),
    )

def render_message_list():
  messages = get_messages()
  return Div(
    *[render_message(entry) for entry in messages],
    id="message-list",
  )

def render_content():
  form = Form(
    Fieldset(
        Input(
          type='text',
          name='name', 
          placeholder='Naam',
          required=True,
          maxlength=MAX_NAME_CHAR,
        ),
        Input(
          type='text',
          name='message', 
          placeholder='Bericht',
          required=True,
          maxlength=MAX_MESSAGE_CHAR,
        ),
        Button("Opslaan", type="submit"),
        role="groep",
    ),
    method="POST",
    hx_post="/submit-message",
    hx_target="#message-list",
    hx_swap="outerHTML",
    hx_on__after_request="this.reset()",
  )

  return Div(
    P(Em("Schrijf iets leuks!")),
    form,
    Div(
      "Gemaakt door ",
      A("Bert", href="http://bertsbieb.nl", target="_blank"),
    ),
    Hr(),
    render_message_list(),
)

@rt("/")
def get():
  return Titled("Bert's gastenboek", render_content())

@rt("/submit-message", methods=["POST"])
def post(name: str, message: str):
  add_message(name, message)
  return render_message_list()

serve()
