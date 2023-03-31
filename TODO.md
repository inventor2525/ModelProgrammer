# TODO (low level)
1. \n's need to be filtered out
1. The headless terminal needs to enter the state it was in on load of conversation
> Thinking this could be as simple as saving a manually entered startup script for the conversation.
1. Reduce context size where possible
	1. Add buttons for canned strings to paste when selecting message text, like "[Output Truncated]" 
	1. Add message version arrows (prev and next version) to play with context construction and summarization methods
	1. Add insert button before send for when selected single item
	> This combined with the canned phrases would allow 
1. Needs parsing capabilities for terminal commands rather than relying on a totally terminal command response
	> assistant needs to be able to talk back (and form 'thoughts'), [Wolverine](https://github.com/biobootloader/wolverine) solved this by having the assistant reply in json, but would like to not do that as it's a lot of extra tokens.
1. Clean up of terminal messages, theres a lot of formatting text in them still and I'd like to actually use it to properly color the terminal output using a special message view for terminal 'replies'

1. view terminal output live using a special message view
1. disable view for message that was just "sent" until a response is back

1. make it commit all changes to fields when sending if there are any un-saved

1. stop selecting what I don't want in the drop down
1. fix scroll view showing up for no lines in text box
1. fix jumpy height of message text boxes

1. speech to text
1. text to speech


# Unsorted:

1. date times need to be maintained properly when loading
1. duplicate messages from different role/names at different send times that have identical content should be recorded in the database as separate messages, currently it's hashed solely by content
1. Add a list of previous conversations, organized by date at first, with editable description.
	1. Add ability to sort them in folders / pin them / or order them
1. Filter conversations in various ways
	1. By those that have the hash(s) of the selected Message(s)
	1. By those that have text in them (a search string or regex)