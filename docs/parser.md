# The Parser:
The parser structure is (with small changes) from Raybert's Post https://groups.google.com/g/rec.arts.int-fiction/c/Y-S-bBojK7E/m/e-xy-z6WRfUJ

The sentences are imperative (The Implied subject is "I").
The sentence structure is:

\<verb>\<object>


## First stage:
Put Words into a list. (by splitting at spaces), convert all to lower case
Discard Articles

## Second stage:
If an "it" is found, it is replaced with the direct object from the sentence before   
remove classified words from list,
check for ANDs and THENs (they have special functions)
Classify the words:
First word is always a verb
// Verbs are also verbs with verb modifiers so also look at the second and last word to check for modifier (adverb).
Search the rest of the words (except for the last) for a preposition from the preposition list
(If a preposition is found, the word to the left is the direct object, the last word is the indirect object)
if no preposition is found, the last word is the object.
Before every object, there is one adjective allowed.
Check if there are non classified words. If there are, the input could not be interpreted

In sentences with ANDs, the sentence is copied, the verb stays and every new instance gets one of the
objects, that are seperated by the ANDs.  
In sentences with THENs, the sentence gets splited at the then and the two (or more) sentences are
executed one after the other.

If there is no object, the object is the player examples:

```bash
$> look # the player looks
```
## Third stage:
Match the objects in the sentence with game objects
game objects have the verb functions in them, match the verb with its
verb function and execute it, if possible, otherwise throw an error.

