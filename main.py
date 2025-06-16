def handle_app_mention_events(body, logger, say):
    logger.info(body)
    event = body["event"]
    channel = event["channel"]

    if isinstance(chat_platform, SlackPlatform):
        chat_platform.add_reaction(channel=channel, name='hourglass_flowing_sand', timestamp=event["ts"])

    pre_prompt = f"You were just pinged in channel {channel} by a user "

    thread_ts = event.get("thread_ts")
    if thread_ts:
        # presumably we should just make a context object or closure instead
        # from our tools but let's see how well this works...
        pre_prompt += f" from within a thread with thread_ts={thread_ts}. "
    else:
        pre_prompt += " from outside of a thread. "
    pre_prompt += "Here is the user's message: "

    user_prompt = strip_userid(event['text'])
    if user_prompt == "":
        logger.info("got empty command; ignoring...")
        return

    # If in a thread, manage message history using the global thread_chats dict.
    # Otherwise, use empty message history for single messages.
    if thread_ts:
        if thread_ts not in thread_chats:
            thread_chats[thread_ts] = []
        message_history = thread_chats[thread_ts]
    else:
        message_history = []

    response = agent.run(pre_prompt + user_prompt, message_history=message_history)
    message_history.append(response.new_messages())


    chat_platform.send_message(text=response.output, channel=channel, thread_ts=thread_ts or event["ts"])
    if isinstance(chat_platform, SlackPlatform):
        chat_platform.remove_reaction(channel=channel, name='hourglass_flowing_sand', timestamp=event["ts"])
