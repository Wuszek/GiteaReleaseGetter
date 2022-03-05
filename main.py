import os
import requests


class PullRequest:

    def __init__(self):
        self.repository_path = "https://api.github.com/repos/go-gitea/gitea/releases/latest"
        self.latest_release = None
        self.last_saved = None
        self.sha1sum = None
        self.sha256sum = None
        self.md5sum = None

    def get_latest(self):
        self.latest_release = requests.get(f"{self.repository_path}").json()["name"]
        return self.latest_release

    def read_file(self):
        get_saved = [line.split() for line in open(".version", "r+")]
        self.last_saved = get_saved[0][0]
        return self.last_saved

    def write_file(self, latest_release):
        file = open(".version", "r+")
        file.seek(0)
        file.truncate()
        print(latest_release, file=file)

    def git_pull_and_checkout(self):
        if os.path.isdir("spksrc"):
            print("DEBUG : Repo already exists... \t PASS".expandtabs(90))
            pass
        else:
            print("DEBUG : Repo does not exist. Setting up... \t IN PROGRESS".expandtabs(90))
            os.popen(f"git clone https://github.com/Wuszek/spksrc.git && cd spksrc && git remote add "
                     f"upstream https://github.com/SynoCommunity/spksrc.git").read()
            print("DEBUG : Repo setting up...  \t DONE".expandtabs(90))

        # TODO : Uncommented is for testing purposes
        # os.popen(f"cd spksrc && git pull upstream master && git rebase upstream/master && git checkout -b"
        #          f" {self.latest_release}").read()
        print("DEBUG : Updating repository... \t IN PROGRESS".expandtabs(90))
        try:
            os.popen(f"cd spksrc && git pull upstream master && git rebase upstream/master").read()
            print("DEBUG : Updating repository...  \t DONE".expandtabs(90))
        except Exception:
            print("ERROR: Something went wrong while updating repository. \t EXITING".expandtabs(90))

    def create_digest(self, hash_type):
        # TODO: Make sure, that this operation is possible. Try/except or if file exist
        digest = os.popen(f"{hash_type.lower()} {self.latest_release}.tar.gz").read()
        temp = digest.split()
        temp.reverse()
        temp[0] = f"gitea-{self.latest_release}.tar.gz"
        temp.insert(1, hash_type[:-3])
        return " ".join(temp)

    def download_gitea_package(self):
        if os.path.isfile(f"{self.latest_release}.tar.gz"):
            print(f"DEBUG : File {self.latest_release}.tar.gz is already downloaded... \t PASS".expandtabs(90))
            pass
        else:
            print(f"DEBUG : Downloading package... \t IN PROGRESS".expandtabs(90))
            try:
                os.popen(f"wget https://github.com/go-gitea/gitea/archive/refs/tags/"
                         f"{self.latest_release}.tar.gz").read()
                print("DEBUG : Downloading package... \t DONE".expandtabs(90))
            except Exception:
                print("DEBUG : Something went wrong while downloading package. \t EXITING".expandtabs(90))
        try:
            print("DEBUG : Calculating checksums for digest... \t IN PROGRESS".expandtabs(90))
            self.sha1sum = self.create_digest("SHA1SUM")
            self.sha256sum = self.create_digest("SHA256SUM")
            self.md5sum = self.create_digest("MD5SUM")
            print("DEBUG : Calculating checksums for digest... \t DONE".expandtabs(90))
        except Exception:
            print("ERROR: Getting checksums went wrong. \t EXITING".expandtabs(90))
            exit(1)

    def update_digest_file(self):
        # TODO: Insert real path to cross/digest inside spksrc repository.
        if os.path.isfile("digest"):
            file = open("digest", "r+")
            file.seek(0)
            file.truncate()
            file.write(f"{self.sha1sum}\n{self.sha256sum}\n{self.md5sum}\n")
            file.close()
            print("DEBUG : Updating cross/digest file... \t DONE".expandtabs(90))
        else:
            print("ERROR : Something went wrong during cross/digest file update. \t EXITING".expandtabs(90))
            exit(1)

    def update_cross_makefile(self):
        # TODO: Insert real path to cross/Makefile inside spksrc repository.
        if os.path.isfile("Makefile"):
            with open("Makefile", "r+") as file:
                data = file.readlines()
            data[1] = f"PKG_VERS = {self.latest_release[1:]}\n"
            with open("Makefile", "r+") as file:
                file.writelines(data)
            file.close()
            print("DEBUG : Updating Makefile...  \t DONE".expandtabs(90))
        else:
            print("ERROR : Something went wrong during cross/Makefile file update. \t EXITING".expandtabs(90))
            exit(1)

        # TODO: Function to update spk/gitea/Makefile
        # TODO: Function to cleanup - delete tar package
        # TODO: Function to push commit to repo after changes was made
        # TODO: Function to create PR from Wuszek/spksrc to synocommunity/spksrc with correct template
        # TODO: First-run function - ig there is no .version file, make it, fill it, exit.
        # TODO: Ping discord channel if new release is available

    def run(self):
        # TODO: check if Makefile exist = just check if repo is there and if is updated
        if self.get_latest() != self.read_file():
            print(f"DEBUG : Newer version appeared: {self.latest_release}. Executing... \t IN PROGRESS".expandtabs(90))
            self.write_file(self.latest_release)
            self.git_pull_and_checkout()
            self.download_gitea_package()
            self.update_digest_file()
            self.update_cross_makefile()
            print("DEBUG : All jobs finished. \t EXITING".expandtabs(90))
            exit(0)
        else:
            print(f"DEBUG : No update. {self.last_saved} is still latest release... \t EXITING".expandtabs(90))
            exit(0)


gitea_update = PullRequest()
gitea_update.run()
