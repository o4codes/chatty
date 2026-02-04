# Feature Ideas

Potential features for Chatty, grouped by category.

## Messaging

- **Typing indicators** — show "Alice is typing..." when someone is composing a message
- **Image/file sharing** — drag-and-drop or paste images, stored temporarily in Redis with the same TTL
- **Reply/quote** — tap a message to reply with the original quoted inline
- **Markdown support** — render bold, italic, code blocks, and links in messages
- **Link previews** — fetch and display Open Graph metadata for shared URLs

## Room Controls

- **Room creator controls** — kick users, set a custom room TTL at creation (15m, 30m, 1h, 4h)
- **Room passwords** — optionally require a password to join
- **Max participants** — set a cap on how many users can be in a room
- **Pinned messages** — let any user pin an important message to the top

## UX Polish

- **Sound notifications** — play a subtle sound on new messages when the tab is in the background
- **Browser notifications** — request permission and show desktop notifications for new messages
- **Unread count in tab title** — show "(3) Chatty" when messages arrive in a background tab
- **Message reactions** — click a message to add a quick emoji reaction
- **Scroll-to-bottom button** — show a floating button when the user has scrolled up with a new message count badge

## Privacy and Moderation

- **End-to-end encryption** — encrypt messages client-side so the server only relays ciphertext
- **Profanity filter** — optional toggle to filter inappropriate language
- **Report/block user** — hide messages from a specific user locally

## Fun

- **GIF search** — integrate Tenor or Giphy API for inline GIF sharing
- **Polls** — create quick yes/no or multiple-choice polls within the chat
- **Slash commands** — `/shrug`, `/tableflip`, `/poll "question" "opt1" "opt2"`
