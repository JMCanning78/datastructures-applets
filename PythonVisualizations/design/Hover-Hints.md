# Showing hints when users hover mouse over controls

To provide some documentation on buttons and the arguments to operations,
we plan to display documentation strings.  There are several kinds.

 * When the Operations panel is first built, we show a label next to
   the text entry widgets that describes what to type in them.  We
   call this the _initial entry hint_.

 * When users allow the mouse to hover over an operations button,
   a line of text describing the operation is displayed in the output
   message line.  We call this an _operation hint_.

 * When users allow the mouse to hover over a text entry widget,
   a line of text describing the argument that goes in that entry
   widget is displayed in the output message line.  We call this
   an _argument hint_.

The initial entry hint is contsructed from the individual argument
hints. The phrase: "Click to enter " is prefixed to the entry hint(s)
provided for the argument(s).  Examples:

 1. Single argument - the key for insertion, deletion, search, etc.
    The argument hint is "item key".  The initial entry hint is
    `Click to enter item key`.  This is all on one line.

 2. Multiple arguments - The first argument is either the string
    to insert or search or the number of strings that will be stored.
    The second is the number of hash functions.  The third is the
    false positive rate for a Bloom filter.  The three hints are:

    *  string or number of strings
    *  number of hashes
    *  false positive rate 0.0 - 0.9

    The initial entry hint spans 3 lines:

```
    "Click to enter string or number of strings,
               number of hashes,
         false positive rate 0.0 - 0.9"
```

## Arming, disarming, and triggering hints

### Initial Entry Hint

The initial entry hint appears when the Operations panel is built
and disappears when clicked or when focus enters any text entry
widget.

### Operation Hint

The operation hint is armed when the cursor enters the region of its
button in the Operations panel.  It is disarmed when the button is
clicked, or when the cursor leaves the region of the button.  It is
triggered when a delay (~1 second) elapses after arming with no
intervening disarming event.  The message is erased automatically at
the start of the operation by the pre-operation call to `cleanUp()` or
by other new messages.

### Argument Hint

The argument hint is armed when the cursor enters the region of its
text entry in the Operations panel.  It is disarmed when a key is
pressed with focus on the text entry, or when the cursor leaves the
region of the entry.  It is triggered when a delay (~1 second) elapses
after arming with no intervening disarming event.  The message is
erased automatically at the start of the operation by the
pre-operation call to `cleanUp()` or by other new messages.

## Implementation

### Initial Entry Hint

The intial entry hint is implemented as a Label widget that is mapped
by putting it in a grid cell of the Operations panel.  The label has
a callback for `<Button>` events that destroys it.  A separate callback
on `<FocusIn>` events in any of the text entry widgets also destroys it.

### Operation and Argument Hints

Tk has `<Enter>` and `<Leave>` events in addition to the `<FocusIn>`,
`<KeyRelease>`, and `<Button>` events that are more widely used.  The
`<Enter>` event is bound to a callback handler that "arms" the hint.
Arming a hint means calling the `after()` method on the widget that
has been entered to create a timeout callback.  That timeout callback
has an ID that gets stored in the widget's 'timeout_ID' attribute.
When the timeout expires, the handler is called to put the message in
the message area.  Separate handlers for `<Leave>`, `<Button>`, and
`<KeyRelease>` are invoked to look for the 'timeout_ID' attribute and
call the `after_cancel()` method on the widget if the ID is set.  They
clear the ID before exiting.