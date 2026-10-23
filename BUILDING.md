# Building Dot Reader

The `.msi` has to be built on Windows and the `.dmg` on macOS. The steps are the same as for Dot Clock.

## Option A: GitHub Actions

There are two separate workflows, so a slow Mac build never holds up the Windows one:

| Workflow | Makes | File |
|---|---|---|
| **Build Windows installer** | `.msi` | `.github/workflows/build.yml` |
| **Build macOS installer** | `.dmg` (Intel + Apple Silicon) | `.github/workflows/build-macos.yml` |

1. Push this folder to its own GitHub repository, for example `dot-reader`.
2. Go to **Actions**, pick a workflow on the left, and click **Run workflow**.
3. Open the run, scroll to the bottom of its Summary page, and download the installer from **Artifacts**.

Pushing a tag such as `v1.0.0` also builds the Windows `.msi` and puts it in a draft GitHub release.

## Option B: build locally

### Windows (makes the .msi)

1. Install the tools once, from Terminal. Skip this if you've already built one of the other apps on this PC:

   ```powershell
   winget install OpenJS.NodeJS.LTS
   winget install Rustlang.Rustup
   winget install Microsoft.VisualStudio.2022.BuildTools --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
   ```

2. Open a terminal in this folder. In File Explorer, type `powershell` in the address bar of the folder that contains `package.json`.
3. Run:

   ```powershell
   npm install
   npm run build:win
   ```

4. The installer is written to `src-tauri\target\release\bundle\msi\Dot Reader_1.0.0_x64_en-US.msi`.

### macOS (makes a universal .dmg)
 
1. Install the tools once, from Terminal. Skip any you already have.
 
   Xcode command line tools:
   ```
   xcode-select --install
   ```

   Rust. If you previously installed Rust through Homebrew, remove it first, because its older Cargo can't build this project and it conflicts with rustup:
   ```
   brew uninstall rust
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```
   Choose the standard installation, then load Rust into your current shell (or just open a new Terminal window):
   ```
   . "$HOME/.cargo/env"
   ```
 
   Node.js (with [Homebrew](https://brew.sh)):
   ```
   brew install node
   ```
   Or download the LTS installer from https://nodejs.org and open a new Terminal window afterwards.
 
   Check everything is in place. Each command should print a version, and `cargo` should be 1.85 or newer:
   ```
   node -v
   npm -v
   cargo --version
   rustup --version
   ```
 
2. Open Terminal in the project folder, the one that contains `package.json`. Type `cd ` (with a trailing space), drag the folder from Finder into the Terminal window and press Enter. For example:
   ```
   cd /Users/yourname/Downloads/dot-[widghetname]-main
   ```
 
3. Add the two Mac build targets and install the dependencies:
   ```
   rustup target add aarch64-apple-darwin x86_64-apple-darwin
   npm install
   ```
 
4. Build. The first run compiles a lot of Rust and can take several minutes:
   ```
   CI=true npm run build:mac
   ```
   `CI=true` skips the step where the DMG script uses AppleScript to arrange the window in Finder. That step can hang or fail depending on Automation permissions. The only effect is that the DMG window has no custom icon layout.
 
5. Open the output folder:
   ```
   open src-tauri/target/universal-apple-darwin/release/bundle/dmg/
   ```
   The installer is `Dot WIDGETNAME_X.X.X_universal.dmg`. If you only see `bundle_dmg.sh` and `icon.icns`, the build didn't finish; see Troubleshooting below.
 
### Troubleshooting (macOS)
 
- **`rustup: command not found`**: run `. "$HOME/.cargo/env"` or open a new Terminal window.
- **`npm: command not found`**: Node.js isn't installed; see step 1.
- **`feature edition2024 is required` / Cargo 1.84**: an old Homebrew Rust is being used instead of rustup's. Run `brew uninstall rust`, open a new Terminal window and check that `cargo --version` is 1.85 or newer.
- **No `.dmg` in the folder, and a "Dot WIDGET" disk is mounted**: a previous build was interrupted. Eject it with `hdiutil detach "/Volumes/Dot WIDGET"` (add `-force` if it's busy), then rebuild with `CI=true npm run build:mac`.

For development, `npm run dev` runs the app with live reload. `npm test` runs the logic tests in Node, which cover the lower-case letters, cleaning up quotes and accents, word wrapping (and breaking very long words), links, lists, the top bar, scrolling, loading and errors, margins at every size, addresses and settings repair.

## Project layout

```
src/                 UI (no build step)
  index.html         the widget window
  settings.html      the settings window
  js/reader.js       the upper + lower case dot font, laying out articles, drawing the widget
  js/extract.js      a downloaded page -> reading-mode blocks (Readability, or a built-in finder)
  js/vendor/         Mozilla Readability, copied from node_modules before each build
  js/dotmatrix.js    5×7 font, Dot Clock's layout, the row + loading bar
  js/worldtime.js    reads Dot Clock's settings and measures its widget
  js/time.js         time-zone helpers (needed to measure Dot Clock's rows)
  js/store.js        settings model + bridge to the native shell
src-tauri/           native shell (Rust), config, icons, capabilities
tools/               icon generator, preview builder
tests/               Node tests
```

## Things to know

- **The link to Dot Clock is by identifier.** "Match Dot Clock" finds Dot Clock's settings using its app identifier, `app.worldtime.dotmatrix`. If you change that identifier in Dot Clock's `tauri.conf.json`, also change `WORLD_TIME_ID` at the top of `src-tauri/src/lib.rs` here.
- **Readability is copied in automatically.** `npm install` downloads Mozilla Readability, and `tools/vendor.js` copies it into `src/js/vendor/` before every `tauri dev` / `tauri build` (`beforeBuildCommand`). If it's missing, Dot Reader still works using its own simpler article finder. The copied file is in `.gitignore`.
- **Pages are downloaded by Rust** (`fetch_page` in `src-tauri/src/lib.rs`, using the `ureq` library), so websites can't block the widget the way they block other sites' scripts. Only http/https addresses are allowed, pages are capped at 8 MB, and their scripts never run.
- **The installers aren't code-signed.** As with Dot Clock, Windows will show a SmartScreen warning and macOS needs **Privacy & Security › Open Anyway**.
- **Replace the placeholder identifier** `app.worldtime.dotreader` in `src-tauri/tauri.conf.json` if you like.
