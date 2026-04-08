"""This is the parser, it converts the user
input into a command, that can be used by the
game."""

import dataclasses
import logging

# configure logging:
logger = logging.getLogger(__name__)

class Parser():

    def __init__(self, game_state, language: str="en"):
        self._game_state = game_state
        # The language as a two letter language code:
        self._language: str = language.lower()
        self._articles: list = self.load_words(
            f"parser/articles_{self._language}"
            )
        self._verbs: list = self.load_words(f"parser/verbs_{self._language}")
        self._verb_modifiers: list = self.load_words(
            f"parser/verbmodifiers_{self._language}"
            )
        self._adjectives: list = self.load_words(
            f"parser/adjectives_{self._language}"
            )

    def load_words(self, file_path: str):
        words: list[str] = []
        with open(file_path, "r", encoding="utf-8") as reader:
            line = reader.readline()
            while line:
                words.append(line)
                line = reader.readline()
        return words

    def handle_then(self, command: list):
        raise NotImplementedError

    def handle_and(self, command: list):
        raise NotImplementedError

#########################
## The actual parsing: ##
#########################

    def stage_two(self, input_command: list):
        """Classify the words from the command."""
        # TODO: Implement "it" functionality
        # remove articles:
        command: list = [
            token for token in input_command
            if not token in self._articles
            ]
        # The command checker is used to keep track
        # of the words, that have been already
        # classified. If the command checker contains
        # any False entries in the end, the classification
        # of some words has failed and an error is raised.
        command_checker: list[bool] = [False for _ in command]
        # handle thens and ands
        if "then" in command:
            self.handle_then(command)
        if "and" in command:
            self.handle_and(command)
        verb: str = command[0]
        logger.debug("Verb at beginning of stage 2: %s", verb)
        command_checker[0] = True
        # verb modifier shows if and where there is a verb modifier in the command
        verb_modifier: int = 0
        if len(command) > 1:
            if f"{verb}_{command[1]}" in self._verbs:
                verb = f"{verb}_{command[1]}"
                command_checker[1] = True
                verb_modifier = 1
            elif f"{verb}_{command[-1]}" in self._verbs:
                verb = f"{verb}_{command[-1]}"
                command_checker[-1] = True
                verb_modifier = -1
        # The verb_modifier range is the range, in
        # which there can be a verb_modifier within the
        # command.
        # The direct object is directly in before the
        # verb_modifier. Because the verb is at position 0,
        # the first place a verb_modifier can be is position 2.
        # If the verb modifier is at position 1 the first
        # possible position for the verb_modifier is there for
        # position 3.
        # The indirect object follows the verb_modifier, so
        # the last position the verb_modifier can be is -2.
        # If the verb modifier is in the last place, the
        # indirect object comes before that and so the last
        # possible position for the verb_modifier is -3.
        verb_modifier_range: list = [2, -2]
        if verb_modifier == 1:
            verb_modifier_range[0] = 3
        elif verb_modifier == -1:
            verb_modifier_range[1] = -3
        # because there is only one verb_modifier, the search
        # for prepostitions ends after the verb_modifier is found.
        verb_modifier_index: int = None
        for prep in self._verb_modifiers:
            if prep in command[verb_modifier_range[0]:verb_modifier_range[1]]:
                verb_modifier_index = command.index(prep)
                command_checker[verb_modifier_index] = True
                break
        if verb_modifier_index:
            logger.debug("A verb_modifier has been found")
            # calculate index for direct object noun:
            direct_object_noun = command[verb_modifier_index -1]
            command_checker[verb_modifier_index -1] = True
            # check for direct object adjective:
            direct_object_adjective = command[verb_modifier_index -2]
            if direct_object_adjective in self._adjectives:
                command_checker[verb_modifier_index -2] = True
            else:
                direct_object_adjective = None
            # claculate index for indirect object noun:
            if not verb_modifier == -1:
                indirect_object_noun = command[-1]
                command_checker[-1] = True
            else:
                indirect_object_noun = command[-2]
                command_checker[-2] = True
            # check for adjective in the indirect object:
            indirect_object_adjective = command[command.index(indirect_object_noun) -1]
            if indirect_object_adjective in self._adjectives:
                command_checker[command.index(indirect_object_adjective)] = True
            else:
                indirect_object_adjective = None
            # Now all parts of the command should have been found.
            # If there are still words in the command, which have
            # no been classified, there is a problem with the
            # structure of the sentence. In this case an error is raised.
            # This is controled by checking the command checker variable.
            for i in command_checker:
                if not i:
                    return "Error, not all words could be clasified."
            command_object = Command(
                    verb,
                    {"adjective": direct_object_adjective,
                    "noun": direct_object_noun},
                    {"adjective": indirect_object_adjective,
                    "noun": indirect_object_noun}
                    )
            return command_object

        # the sentence has no verb modifiers
        # calculate the position of the direct object noun:
        if not verb_modifier == -1:
            direct_object_noun = command[-1]
            command_checker[-1] = True
        else:
            direct_object_noun = command[-2]
            command_checker[-2] = True
        # check for a adjective in the direct object:
        direct_object_adjective = command[command.index(direct_object_noun) -1]
        if direct_object_adjective in self._adjectives:
            command_checker[command.index(direct_object_adjective)] = True
        else:
            direct_object_adjective = None
        # Now all parts of the command should have been found.
        # Since the command has no verb modifiers,
        # it has no indirect object.
        logger.debug(f"Command checker: {command_checker}")
        logger.debug(f"command  source: {command}")
        for i in command_checker:
            if not i:
                logger.warning(
                    "End of stage two, not all words could be classified"
                    )
                return "Warning: not all words could be clasified."
        command_object = Command(
                    verb,
                    {"adjective": direct_object_adjective,
                     "noun": direct_object_noun}
                    )
        return command_object

@dataclasses.dataclass
class Command():

    def __init__(self, verb: str, direct_object: dict,
                indirect_object: dict=None
                ):
        self.verb: str = verb
        self.direct_object: dict = direct_object
        self.indirect_object: dict = indirect_object
