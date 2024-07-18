def generate_message(game_links):
    table_messages = ""
    for index, table_link in enumerate(game_links):
        table_messages += f"Table {index+1}: {table_link}\n"
    table_messages = table_messages.strip()
    user_id = 123
    
    response_message = (
        f"Game Hosted By: <@{user_id}>\n\n"
        f"{table_messages}\n\n"
        f"# Stakes: **{'.25/.50'}**\n\n"
        f"**Venmo: @{'xpoes'}**\n"
        f"**Cashapp: ${'bamboobino'}**\n\n"
        f"<@&{'test'}>\n"
    )
    
    return response_message

print(generate_message(["test1", "test2", "test3"]))
