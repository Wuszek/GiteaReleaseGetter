import os
import subprocess
from subprocess import check_output
import requests


class PullRequest:

    def __init__(self):
        self.repository_path = "https://api.github.com/repos/go-gitea/gitea/releases/latest"
        self.latest_release = None
        self.last_saved = None
        self.sha1sum = None
        self.sha256sum = None
        self.md5sum = None
        self.webhook = None  # insert "webhook url address"

    def get_latest(self):
        self.latest_release = requests.get(f"{self.repository_path}").json()["name"]
        return self.latest_release

    def read_version(self):
        if os.path.isfile(".version"):
            get_saved = [line.split() for line in open(".version", "r+")]
            self.last_saved = get_saved[0][0]
            return self.last_saved
        else:
            file = open(".version", "w")
            print(self.latest_release, file=file)
            print("DEBUG : No .version file. Creating and filling one... \t DONE".expandtabs(90))
            exit("DEBUG : First run finished. \t EXITING".expandtabs(90))

    @staticmethod
    def discord_notify_setup(self):
        if os.path.isfile("discord.sh"):
            return True
        else:
            try:
                print("DEBUG : 'discord.sh' script is not present. Downloading... \t IN PROGRESS".expandtabs(90))
                filename = "discord.sh"
                url = 'https://raw.githubusercontent.com/ChaoticWeg/discord.sh/master/discord.sh'
                f = requests.get(url)
                open(filename, 'wb').write(f.content)
                os.popen('chmod +x discord.sh').read()
                print("DEBUG : 'discord.sh' script downloaded. \t DONE".expandtabs(90))
                return True
            except Exception:
                print("ERROR : Something went wrong while downloadind script. \t EXITING".expandtabs(90))

    def discord_notify(self):
        if self.discord_notify_setup():
            command = f'./discord.sh \
                        --webhook-url="{self.webhook}" \
                        --username "GiteaBot" \
                        --avatar "https://docs.gitea.io/images/gitea.png" \
                        --text "**NEW GITEA UPDATE!** \\nRelease: {self.latest_release}"'
            msg = os.popen(command).read()
            if "fatal" in msg:
                print("ERROR : Something went wrong while running 'discord.sh' (webhook?). \t PASS".expandtabs(90))
            else:
                print("DEBUG : Discord message sent successfully. \t DONE".expandtabs(90))

    @staticmethod
    def write_version(self, latest_release):
        if os.path.isfile(".version"):
            file = open(".version", "r+")
            file.seek(0)
            file.truncate()
            print(latest_release, file=file)
        else:
            exit("ERROR: Something in writing .version file function went wront. \t EXITING".expandtabs(90))

    @staticmethod
    def git_pull_and_checkout(self):
        if os.path.isdir("spksrc"):
            print("DEBUG : Repo already exists... \t PASS".expandtabs(90))
            pass
        else:
            print("DEBUG : Repo does not exist. Setting up... \t IN PROGRESS".expandtabs(90))
            os.popen(f"git clone https://github.com/Wuszek/spksrc.git && cd spksrc && git remote add "
                     f"upstream https://github.com/SynoCommunity/spksrc.git").read()
            print("DEBUG : Repo setting up...  \t DONE".expandtabs(90))

        print("DEBUG : Updating repository... \t IN PROGRESS".expandtabs(90))
        try:
            os.popen(f"cd spksrc && git restore . && git pull upstream master && git rebase upstream/master").read()
            # TODO : Uncommented is for testing purposes
            # os.popen(f"cd spksrc && git pull upstream master && git rebase upstream/master && git checkout -b"
            #          f" {self.latest_release}").read()
            print("DEBUG : Repository updated successfully.  \t DONE".expandtabs(90))
        except Exception:
            print("ERROR : Something went wrong while updating repository. \t EXITING".expandtabs(90))

    def create_digests(self, hash_type):
        if os.path.isfile(f"{self.latest_release}.tar.gz"):
            digests = os.popen(f"{hash_type.lower()} {self.latest_release}.tar.gz").read()
            temp = digests.split()
            temp.reverse()
            temp[0] = f"gitea-{self.latest_release}.tar.gz"
            temp.insert(1, hash_type[:-3])
            return " ".join(temp)
        else:
            exit(f"ERROR: Package {self.latest_release}tar.gz doesn't exist. \t EXITING".expandtabs(90))

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
            print("DEBUG : Calculating checksums for digests... \t IN PROGRESS".expandtabs(90))
            self.sha1sum = self.create_digests("SHA1SUM")
            self.sha256sum = self.create_digests("SHA256SUM")
            self.md5sum = self.create_digests("MD5SUM")
            print("DEBUG : Calculating checksums for digests... \t DONE".expandtabs(90))
        except Exception:
            print("ERROR: Getting checksums went wrong. \t EXITING".expandtabs(90))
            exit(1)

    def update_digests_file(self):
        if os.path.isfile("spksrc/cross/gitea/digests"):
            file = open("spksrc/cross/gitea/digests", "r+")
            file.seek(0)
            file.truncate()
            file.write(f"{self.sha1sum}\n{self.sha256sum}\n{self.md5sum}\n")
            file.close()
            print("DEBUG : Updating cross/gitea/digests file... \t DONE".expandtabs(90))
        else:
            exit("ERROR : Something went wrong during cross/gitea/digests file update. \t EXITING".expandtabs(90))

    def update_cross_makefile(self):
        if os.path.isfile("spksrc/cross/gitea/Makefile"):
            with open("spksrc/cross/gitea/Makefile", "r+") as file:
                data = file.readlines()
            data[1] = f"PKG_VERS = {self.latest_release[1:]}\n"
            with open("spksrc/cross/gitea/Makefile", "r+") as file:
                file.writelines(data)
            file.close()
            print("DEBUG : Updating cross/gitea/Makefile...  \t DONE".expandtabs(90))
        else:
            exit("ERROR : Something went wrong during cross/gitea/Makefile file update. \t EXITING".expandtabs(90))

    def update_gitea_makefile(self):
        if os.path.isfile("spksrc/spk/gitea/Makefile"):
            with open("spksrc/spk/gitea/Makefile", "r+") as file:
                data = file.readlines()
            data[1] = f"PKG_VERS = {self.latest_release[1:]}\n"
            revision = int(data[2][10:]) + 1
            data[2] = f"SPK_REV = {revision}\n"
            data[8] = f'''{data[8][:-2]}<br/> {revision}. Update to {self.latest_release}."\n'''
            with open("spksrc/spk/gitea/Makefile", "r+") as file:
                file.writelines(data)
            file.close()
            print("DEBUG : Updating spk/gitea/Makefile...  \t DONE".expandtabs(90))
        else:
            exit("ERROR : Something went wrong during spk/gitea/Makefile file update \t EXITING".expandtabs(90))

    @staticmethod
    def cleanup(self, latest):
        if os.path.isfile(f"{latest}.tar.gz"):
            try:
                check_output(["rm", f"{latest}.tar.gz"])
                print(f"DEBUG : Removing {latest}.tar.gz from {os.getcwd()}... \t DONE".expandtabs(90))
            except subprocess.CalledProcessError:
                print(f"ERROR : Couldn't delete {latest}.tar.gz file. \t PASS".expandtabs(90))
                pass
        else:
            print("DEBUG : There is nothing to delete and nothing happens. \t PASS".expandtabs(90))
            pass

        # TODO: Uncomment git_pull_and_checkout operation 
        # TODO: Function to push commit to repo after changes was made
        # TODO: Function to create PR from Wuszek/spksrc to synocommunity/spksrc with correct template

    def run(self):
        if self.get_latest() != self.read_version():
            print(f"DEBUG : Newer version appeared: {self.latest_release}. Executing... \t IN PROGRESS".expandtabs(90))
            self.discord_notify()
            self.write_version(self.latest_release)
            self.git_pull_and_checkout()
            self.download_gitea_package()
            self.update_digests_file()
            self.update_cross_makefile()
            self.update_gitea_makefile()
            self.cleanup(self.latest_release)
            print("DEBUG : All jobs finished. \t EXITING".expandtabs(90))
            exit(0)
        else:
            print(f"DEBUG : No update. {self.last_saved} is still latest release... \t EXITING".expandtabs(90))
            exit(0)


gitea_update = PullRequest()
gitea_update.run()
