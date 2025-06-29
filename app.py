from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from bot import TeamsBot
from botbuilder.schema import Activity
import asyncio

APP_ID="APP_ID"
APP_PASSWORD="APP_PASSWORD"  # Replace with your actual app password
app = Flask(__name__)
# adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter_settings = BotFrameworkAdapterSettings("","")
adapter = BotFrameworkAdapter(adapter_settings)
bot = TeamsBot()

@app.route("/snapshot", methods=["POST"])
def messages():
    try:
        if "application/json" not in request.headers.get("Content-Type", ""):
            return Response("Unsupported Media Type", status=415)

        body = request.json
        print("Incoming body:", body)  # Optional debug
        activity = Activity().deserialize(body)
        print("Authorization header:", request.headers.get("Authorization"))
        print("Received activity:", activity.type)
        auth_header = request.headers.get("Authorization", "")

        async def call_bot():
            await adapter.process_activity(activity, auth_header, bot.on_turn)

        asyncio.run(call_bot())
        return Response("Message processed successfully", status=200)

    except Exception as e:
        print("Error processing activity:", str(e))
        return Response(f"Internal Server Error: {str(e)}", status=500)

if __name__ == "__main__":
    app.run(port=3978, debug=True)