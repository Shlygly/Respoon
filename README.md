# Respoon
Automatic response manager addon for Hexchat

## Usage

Add an automatic response :
`/RESPOON ADD <message> {*|#<channel>} <response>`

Remove an automatic response :
`/RESPOON DEL <ID>`

Edit an automatic reponse :
`/RESPOON EDIT <ID> <message> {*|#<channel>} <response>`

List all automatic reponses :
`/RESPOON LIST`

## Examples

`/RESPOON ADD Hello #mychannel Welcome`

`/RESPOON ADD "Who wants a muffin ?" * "Me !"`

`/RESPOON EDIT 2 "Who wants a muffin ?" * "Not anymore !"`

`/RESPOON DEL 1`
