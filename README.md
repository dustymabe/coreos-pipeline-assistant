# CoreOS Pipeline Assistant

This is an AI-powered assistant used by the CoreOS team to make pipeline monitoring easier.
Currently, it only works in Slack, but in the future it will also be pluggable into Matrix.

The assistant listens for direct mentions in a Slack channel in which it was invited.

Currently, it can:
- retrieve overall pipeline health status
- retrieve generic build information (stream, version, architectures, status)
- retrieve build logs, analyze them, and provide a summary of failures
- retry builds

## Setup

### Local Python Environment

1.  **Install dependencies:**
    ```
    source env/bin/activate  # if using a virtualenv
    pip install -r requirements.txt
    ```

2.  **Set environment variables:**
    *   `MATRIX_HOMESERVER_URL`: Your homeserver (i.e.  https://matrix.org)
    *   `MATRIX_ACCESS_TOKEN`: Your device access token
    *   `MATRIX_ROOM`: Your room FQDN (i.e. `#tmp-coreos-pipeline-assistant-testing:matrix.org`)
    *   `JENKINS_URL`: The URL of your Jenkins server.
    *   `JENKINS_TOKEN`: Your Jenkins token (often an API token).
    *   `OPENROUTER_API_KEY`: Your OpenRouter access key
    *   `CHAT_PLATFORM=matrix`: set to matrix for now

## Usage

1.  **Run the bot:**
    ```
    source env.sh            # tokens env vars
    source env/bin/activate  # if using a virtualenv
    python main.py
    ```

2.  **Invite the bot to your Slack channel.**

3.  **Mention the bot in a thread of a Jenkins failure notification.** The bot will then reply with a summary of the failure.

### Running with Podman

1.  **Build the container image:**
    ```
    podman build -t coreos-pipeline-assistant .
    ```

2.  **Run the container:**
    You can pass the environment variables directly with the `-e` flag, or you can use a `.env` file.

    **Using a `.env` file:**
    Create a file named `.env` with the following content:
    ```
    MATRIX_HOMESERVER_URL=https://matrix.org
    MATRIX_ACCESS_TOKEN=your_app_token
    MATRIX_ROOM=your_room_fqdn
    JENKINS_URL=https://your.jenkins.url
    JENKINS_TOKEN=your_jenkins_token
    OPENROUTER_API_KEY=your_api_key
    CHAT_PLATFORM=matrix
    ```
    Then run the container with the `--env-file` flag:
    ```
    podman run -it --rm --env-file .env coreos-pipeline-assistant
    ```

## Testing

To run the unit tests, run the following command from the root of the project:
```
python3 test.py
```
