# Serves the web build locally, for trying it out: nix run .#serve-web
# (optionally followed by a port). Browsers do not run WebAssembly from
# file:// pages, so the site must come from an HTTP server.
#
# Files in the Nix store all have the same modification time, so a plain
# http.server tells browsers that their cached copy of index.html is still
# current after a rebuild. This server tells them not to cache.
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
    exec python3 ${./serve-web.py} ${pigeoncide-web} "$port"
  '';
}
