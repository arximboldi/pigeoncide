# Serves the web build locally, for trying it out: nix run .#serve-web
# (optionally followed by a port). Browsers do not run WebAssembly from
# file:// pages, so the site must come from an HTTP server.
{
  writeShellApplication,
  python3,
  pigeoncide-web,
}:

writeShellApplication {
  name = "serve-web";
  runtimeInputs = [ python3 ];
  text = ''
    port="''${1:-8000}"
    echo "Serving Pigeoncide at http://localhost:$port/"
    exec python3 -m http.server --bind 127.0.0.1 --directory ${pigeoncide-web} "$port"
  '';
}
