import json
import os.path


class Config:
    """A named configuration file.

    ONLY FOR NON-SECURE DATA because this data is kept in the running directory
    which may be inside the git repository.
    High-security data should be dealt with by {handy_display.Secrets}.

    Entries are read from `config/{name}.json`, where `name` is passed to the constructor.

    Implements __getitem__ and __setitem__ to support '["key"] = value' syntax.
    """

    def __init__(self, name: str, default: dict[str, object]):
        """Create a new Config object.
        :param name: The name of the configuration file. Will be created at `config/{name}.json`
        :param default: Default values for the configuration. Will be automatically populated
        if they don't exist.
        """

        self._name: str = name
        self._default: dict[str, object] = default

        self._path = "config/{name}.json".format(name=self._name)
        self._entries: dict[str, object] = {}

        self.reload()

    def reload(self):
        """Reload configuration entries from disk.
        Also calls {self.save()}, which populates default values in file.
        :return: Nothing.
        """

        print("Reloading '{name}' config... ".format(name=self._name))

        if not os.path.exists("config/"):
            print("Creating config/ directory...")
            os.mkdir("config/")

        if not os.path.exists(self._path):
            default_contents = json.dumps(self._default, indent=4)
            with open(self._path, "x") as config:
                config.write(default_contents)

        try:
            with open(self._path, "r") as config:
                self._entries = json.load(config)
        except json.decoder.JSONDecodeError as jde:
            print("")
            print("Error deserializing file '{path}'. Probably a malformed JSON or empty file."
                  .format(path=self._path))
            print(" >> " + str(jde))
            exit(438943)

        self.save()

    def save(self):
        """Save the values stored in memory to disk.
        Also populates default values.
        :return: Nothing.
        """

        needs_saving = False
        for k, v in self._default.items():
            if k not in self._entries:
                self._entries[k] = v
                needs_saving = True
        if needs_saving:
            with open(self._path, 'w') as config:
                contents = json.dumps(self._entries, indent=4)
                config.write(contents)

    def __getitem__(self, item):
        if item in self._entries:
            return self._entries[item]
        raise IndexError("The key '{key}' does not exist in the configuration object '{name}'"
                         .format(key=item, name=self._name))

    def __setitem__(self, key, value):
        self._entries[key] = value
