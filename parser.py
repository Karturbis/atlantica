"""This is the parser, it converts the user
input into a command, that can be used by the
game."""
class Parser():

    def __init__(self, language: str="en"):
        """The language as a two letter language code."""
        self._language: str = language.lower()
        self._articles: list = self.load_words(f"parser/articles_{self._language}")
        self._verbs: list = self.load_words("parser/verbs")
        self._prepositions: list = self.load_words(f"parser/prepositions_{self._language}")
        self._adjectives: list = self.load_words(f"parser/adjectives_{self._language}")

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
########################

    def stage_one(self, input_str:str, aliases: dict) -> list :
        """Convert the input string into a list of words"""
        # replace aliases with their values:
        for key, value in aliases.items():
            input_str = input_str.replace(key, value)
        # convert string into list of lower case words:
        return input_str.lower().split()

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
        command_checker[0] = True
        # verb modifier shows if and where there is a verb modifier in the command
        verb_modifier: int = 0
        if f"{verb}_{command[1]}" in self._verbs:
            verb = f"{verb}_{command[1]}"
            command_checker[1] = True
            verb_modifier = 1
        elif f"{verb}_{command[-1]}" in self._verbs:
            verb = f"{verb}_{command[-1]}"
            command_checker[-1] = True
            verb_modifier = -1
        # The preposition range is the range, in
        # which there can be a preposition within the
        # command.
        # The direct object is directly in before the
        # preposition. Because the verb is at position 0,
        # the first place a preposition can be is position 2.
        # If the verb modifier is at position 1 the first
        # possible position for the preposition is there for
        # position 3.
        # The indirect object follows the preposition, so
        # the last position the preposition can be is -2.
        # If the verb modifier is in the last place, the
        # indirect object comes before that and so the last
        # possible position for the preposition is -3.
        preposition_range: list = [2, -2]
        if verb_modifier == 1:
            preposition_range[0] = 3
        elif verb_modifier == -1:
            preposition_range[1] = -3
        # because there is only one preposition, the search
        # for prepostitions ends after the preposition is found.
        preposition_index = None
        for prep in self._prepositions:
            if prep in command[preposition_range[0]:preposition_range[1]]:
                preposition_index = command.index(prep)
                command_checker[preposition_index] = True
                break
        if preposition_index:
            # calculate index for direct object noun:
            direct_object_noun = command[preposition_index -1]
            command_checker[preposition_index -1] = True
            # check for direct object adjective:
            direct_object_adjective = command[preposition_index -2]
            if direct_object_adjective in self._adjectives:
                command_checker[preposition_index -2] = True
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
            command_object = Command(verb, [direct_object_adjective, direct_object_noun],
                                    [indirect_object_adjective, indirect_object_noun]
                                    )
            return command_object

        # the sentence is a non prepositional phrase
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
        # Since the command is a non prepositional phrase,
        # it has no indirect object.
        for i in command_checker:
            if not i:
                return "Error, not all words could be clasified."
        command_object = Command(verb, [direct_object_adjective, direct_object_noun])
        return command_object



    def stage_three(self):
        pass


class Command():

    def __init__(self, verb: str, direct_object: list,
                indirect_object: list=None
                ):
        self._verb: str = verb
        self._direct_object: list[str] = direct_object
        self._indirect_object: list[str] = indirect_object