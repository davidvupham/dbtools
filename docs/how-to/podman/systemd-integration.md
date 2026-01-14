# Podman Systemd Integration

Integrating Podman with Systemd allows you to manage containers as native system services. This ensures containers start
at boot, restart on failure, and can be managed with standard `systemctl` commands.

## Methods

There are two primary methods for integrating Podman with Systemd:

1. **Quadlet (Recommended for Podman v4.6+)**: A declarative, file-based approach using `.container` files. It is the
    modern standard for RHEL 9.
2. **`podman generate systemd` (Legacy)**: Generates standard systemd unit files from existing containers. Useful for
    RHEL 8 or older Podman versions.

---

## Method 1: Quadlet (Recommended)

Quadlet allows you to define containers in a simplified format, which a systemd generator then converts into full
service units automatically.

### 1. Create a `.container` file

For a rootless user, create the directory:

```bash
mkdir -p ~/.config/containers/systemd/
```

Create a file named `my-web.container`:

```ini
[Unit]
Description=My Nginx Web Server
After=network-online.target

[Container]
Image=nginx:alpine
PublishPort=8080:80
Exec=nginx -g 'daemon off;'

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### 2. Activate the Service

Reload the systemd daemon (this triggers the generator):

```bash
systemctl --user daemon-reload
```

Start and enable the generated service (note the `.service` extension):

```bash
systemctl --user start my-web.service
systemctl --user enable my-web.service
```

### 3. Verify

```bash
systemctl --user status my-web.service
```

---

## Method 2: `podman generate systemd` (Legacy)

This method involves running a container first, then asking Podman to create a unit file for it.

### 1. Run the Container

```bash
podman run -d --name my-old-web -p 8081:80 nginx:alpine
```

### 2. Generate Unit File

```bash
mkdir -p ~/.config/systemd/user/
cd ~/.config/systemd/user/

# Generate the file
podman generate systemd --name my-old-web --files --new
```

* `--files`: Write to a file instead of stdout.
* `--new`: Create a transient container service (creates on start, removes on stop).

### 3. Enable and Start

```bash
podman stop my-old-web
podman rm my-old-web
systemctl --user daemon-reload
systemctl --user enable --now container-my-old-web.service
```

---

## Auto-Update

Podman and Systemd can work together to automatically update your containers when a new image is available.

1. **Tag the container**: Add the label `io.containers.autoupdate=registry`.
    * In Quadlet: `AutoUpdate=registry` under `[Container]`.
    * In CLI: `--label "io.containers.autoupdate=registry"`.
2. **Enable the timer**:

    ```bash
    systemctl --user enable --now podman-auto-update.timer
    ```

This timer typically runs once per day, checks for newer images, pulls them, and restarts the affected services.
