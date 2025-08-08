# Copyright (C) 2025 Heptazhou <zhou@0h7z.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from base64 import b64decode as base64decode
from builtins import isinstance as isa
from pathlib import Path
from re import sub as replace
from sys import platform as PLATFORM
from time import sleep
from typing import Literal, cast

from selenium.common import TimeoutException
from selenium.webdriver import Firefox, FirefoxOptions, Keys
from selenium.webdriver import Remote as Browser


def isapple() -> bool:
	return PLATFORM == "darwin"

def filesize(f: Path | str) -> int:
	if not isfile(f): return 0
	if isa(f, Path):
		return (f).stat().st_size
	return Path(f).stat().st_size

def isfile(f: Path | str) -> bool:
	if isa(f, Path):
		return (f).is_file()
	return Path(f).is_file()

def write(f: Path | str, x: bytes | str) -> int:
	if isa(x, bytes):
		with open(f, "wb") as io:
			return io.write(x)
	else:
		with open(f, "wt", newline="") as io:
			return io.write(x)

# mypy: disable-error-code="func-returns-value"

if isapple():
	netmonitor = Keys.LEFT_COMMAND + Keys.LEFT_OPTION + "E"
else:
	netmonitor = Keys.LEFT_CONTROL + Keys.LEFT_SHIFT + "E"

def init(headless: bool = False) -> Browser:
	# https://wiki.mozilla.org/Firefox/CommandLineOptions
	opt = FirefoxOptions()
	opt.add_argument("-headless") if headless else None
	opt.set_preference("browser.aboutConfig.showWarning", False)
	opt.set_preference("browser.ctrlTab.sortByRecentlyUsed", True)
	opt.set_preference("browser.link.open_newwindow", 3)
	opt.set_preference("browser.menu.showViewImageInfo", True)
	opt.set_preference("browser.ml.enable", False)
	opt.set_preference("datareporting.usage.uploadEnabled", False)
	opt.set_preference("devtools.netmonitor.persistlog", True)
	opt.set_preference("devtools.selfxss.count", 5)
	opt.set_preference("devtools.webconsole.persistlog", True)
	opt.set_preference("devtools.webconsole.timestampMessages", True)
	opt.set_preference("identity.fxaccounts.enabled", False)
	opt.set_preference("pdfjs.externalLinkTarget", 2)
	opt.set_preference("privacy.fingerprintingProtection.overrides", "+AllTargets,-CanvasRandomization,-CanvasImageExtractionPrompt,-CanvasExtractionBeforeUserInputIsBlocked")
	opt.set_preference("privacy.fingerprintingProtection", True)
	opt.set_preference("privacy.spoof_english", 2)
	opt.set_preference("privacy.window.maxInnerHeight", 900)
	opt.set_preference("privacy.window.maxInnerWidth", 1600)
	opt.set_preference("security.OCSP.enabled", 0)
	opt.set_preference("security.pki.crlite_mode", 2)
	opt.set_preference("sidebar.main.tools", "history")
	ret = Firefox(opt)
	ret.set_page_load_timeout(5)
	ret.set_script_timeout(3)
	ret.set_window_size(1600, 900) if headless else None
	return ret

def load(br: Browser, dr: Literal["edr", "dr1"], id: int | str) -> bytes:
	# https://data.desi.lbl.gov/doc/access/
	br.get(f"https://www.legacysurvey.org/viewer/desi-spectrum/{dr}/targetid{id}")
	js = """return document.querySelector("canvas").toDataURL("image/png")"""
	rv = cast(str, br.execute_script(js))
	br.get(rv)
	rv = replace(r"^data:[^,]*,", "", rv)
	return base64decode(rv)

def save(br: Browser, dr: Literal["edr", "dr1"], id: int | str, path: str | None = None) -> None:
	if path is None: path = f"desi-{dr}-{id}.png"
	br.switch_to.new_window() # new tab
	if filesize(path) > 0: return br.get(Path(path).absolute().as_uri()) # already exists
	br.get("about:logo"), br.switch_to.active_element.send_keys(netmonitor), sleep(1)
	while True:
		try:
			data = load(br, dr, id)
			break
		except TimeoutException: sleep(2)
	write(path, data)

if __name__ == "__main__":
	ff = init()
	save(ff, "dr1", 39627848784286649) # https://www.legacysurvey.org/viewer/desi-spectrum/dr1/targetid39627848784286649
	save(ff, "dr1", 39627848784285507) # https://www.legacysurvey.org/viewer/desi-spectrum/dr1/targetid39627848784285507
	# ff.quit() # close the browser

