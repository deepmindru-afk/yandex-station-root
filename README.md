# Yandex Station root

Enable root ADB through the Station's cloud configuration, keep network ADB active, and disable its
native OTA launcher task.

**Tested only on Station Mini 2 (YNDX-00020), firmware `0.369.1.46.4778262943.20261013.299`.** Other
models and builds are untested. The tested `.50` build rejects the CA chain used here.

## Requirements

- Python 3.13, make, a POSIX shell, and Android platform-tools (`adb`).
- A router that can override DNS or assign a custom DNS server for one device.
- A computer reachable by the Station on TCP ports 80 and 443, plus UDP/TCP 53 if using the DNS
  helper.

Run commands from the repository root:

```sh
make setup
cp config.example.mk config.mk
```

Edit `config.mk`:

| Setting             | Value                                                               |
| ------------------- | ------------------------------------------------------------------- |
| `STATION_IP`        | The Station's current IPv4 address                                  |
| `STATION_DEVICE_ID` | Its Quasar `device_id` from the smart-home app's device information |
| `STATION_PLATFORM`  | Its Quasar platform, `yandexmini_2` for the tested device           |
| `PROXY_IP`          | This computer's LAN IPv4 address                                    |

Use the Quasar identifier, not the web app's device UUID. Check the router's device list after a
factory reset; the Station may use a different MAC or IP address.

Local settings, certificates, and receipts under `private/` are ignored by Git. The bundled
`certs/issuer.*` files are the publicly disclosed compromised CA material from
[Fluepke's disclosure](https://github.com/Fluepke/emudrahahahahaha). `make cert` creates a local
server key and issues a 48-hour certificate. Renewal keeps the key. Do not add this CA to the
computer's trust store.

## Get root

1. Run `make proxy` and leave it running. It renews the certificate and accepts connections only
   from `STATION_IP`.
2. Point these DNS names to `PROXY_IP` for the selected Station:

   ```text
   quasar.yandex.net
   quasar.yandex.ru
   scbh.yandex.net
   ```

   Return no AAAA records for them. The computer running the proxy must resolve the real upstream
   addresses. If the router needs a custom DNS server, run `make dns` in another terminal and assign
   `PROXY_IP` as the Station's DNS server. Prevent the Station from bypassing it. Other queries go
   to Google DNS over verified HTTPS.

3. Keep the Station's internet access and VPN route. Leave other devices' DNS and the router's
   global DNS rebinding protection unchanged.
4. Restart the Station, then run `make connect` and `make status`.

The proxy changes ADB settings only when the source IP, `device_id`, platform, and API path match.
Other configuration fields stay intact. `private/enable_state.json` records the result without
saving authorization headers or the configuration body.

### Factory recovery

On the tested Mini 2, a full reset clears Wi-Fi and account settings. Disconnect power, hold the
microphone-off button while reconnecting power, then release it when the light turns yellow, after
about five seconds. Configure Wi-Fi again in the app.

The tested recovery needed one official update to `.46`. Run `make offer` before activation and keep
the proxy and DNS available. It offers `firmware/update_manifest.json` once through the native
updater. Downloads use the original Yandex URLs. The kit does not serve an image or flash
partitions. The bundled manifest is for Mini 2; changing `STATION_PLATFORM` does not make it
suitable for another model.

The receipt is consumed before delivery. Restarting the proxy does not rearm it, and delivery does
not prove installation. If setup fails, inspect the proxy output and `private/offer_receipt.json`
before deliberately archiving the receipt and running `make offer` again.

## Keep access

Once root ADB is reachable:

```sh
make install
make reboot
make status
```

`install-adb` wraps the native activation script, preserves network activation, and creates the
native boot markers. `disable-updates` reads the Station's current `launch.json` and removes only
the `updatesd` task. `install` runs both commands.

Original files are saved beside the native files under `/system/vendor/quasar/`. The installer
checks script structure and launcher contents before writing. It preserves existing originals,
accepts earlier installations of the same guard, and refuses ambiguous backups or unrelated changes.
These checks establish compatibility with the supported file structure. They do not authenticate the
firmware.

Reboot applies the launcher change. `status` reports its configuration, not whether an updater
process from the current boot is still running. After confirming root following reboot, restore
ordinary DNS and stop the proxy and optional DNS helper with Ctrl+C. Keep the VPN route.

Network ADB on the tested firmware has no key authentication. Keep port 5555 inside a trusted LAN.

## Restore

```sh
make restore-updates
make restore-adb
make reboot
```

Restore uses saved originals and refuses to overwrite unrelated edits. Restoring the ADB script
keeps its activation markers; a later cloud configuration can deactivate ADB again.

Persistence writes use `/data/local/tmp/station-root.lock`. If an interrupted command leaves it
behind, confirm that no installer is running before removing that directory over ADB and retrying.
Do not delete the original-file backups.

## Commands

`make help` lists all targets. Proxy and DNS commands run in the foreground. `make check` validates
source syntax and the bundled manifest without contacting a Station. `make clean` removes the
virtual environment and Python caches, preserving settings and private files.

Override `PYTHON`, `ADB`, or `SUDO` when needed. For unprivileged local runs, set `SUDO=` and choose
`HTTP_PORT`, `HTTPS_PORT`, and `DNS_PORT` above 1024. `LISTEN_HOST` defaults to `0.0.0.0`.
`make dns DNS_DOH=0` forwards other DNS queries over TCP to `DNS_UPSTREAM`, default `8.8.4.4:53`.
