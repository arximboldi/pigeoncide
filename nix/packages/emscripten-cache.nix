# A starting point for a writable Emscripten cache: the system libraries
# prebuilt by nixpkgs plus the Emscripten "ports" (third-party libraries)
# used by the web build. Emscripten would download the ports while
# compiling, which the build sandbox forbids, so they are fetched here, at
# the URLs and hashes the port definitions of this Emscripten version
# give, and unpacked the way Emscripten itself would.
#
# Builds copy this to a writable $EM_CACHE, since Emscripten writes to its
# cache: cp -r --no-preserve=mode <this> "$EM_CACHE".
{
  lib,
  stdenvNoCC,
  fetchurl,
  emscripten,
  unzip,
}:

let
  # From emscripten's tools/ports/<name>.py.
  ports = {
    zlib = {
      url = "https://github.com/madler/zlib/archive/refs/tags/v1.3.2.tar.gz";
      sha512 = "16fea4df307a68cf0035858abe2fd550250618a97590e202037acd18a666f57afc10f8836cbbd472d54a0e76539d0e558cb26f059d53de52ff90634bbf4f47d4";
    };
    bzip2 = {
      url = "https://github.com/emscripten-ports/bzip2/archive/1.0.6.zip";
      sha512 = "512cbfde5144067f677496452f3335e9368fd5d7564899cb49e77847b9ae7dca598218276637cbf5ec524523be1e8ace4ad36a148ef7f4badf3f6d5a002a4bb2";
    };
    sqlite3 = {
      url = "https://www.sqlite.org/2022/sqlite-amalgamation-3390000.zip";
      sha512 = "cbaf4adb3e404d9aa403b34f133c5beca5f641ae1e23f84dbb021da1fb9efdc7c56b5922eb533ae5cb6d26410ac60cb3f026085591bc83ebc1c225aed0cf37ca";
    };
    ogg = {
      url = "https://github.com/xiph/ogg/releases/download/v1.3.5/libogg-1.3.5.zip";
      sha512 = "e7b5f5d469090b66dbb33634591ae6de41af3a5644c10488e59ba7428ed78912e208a2c0fbb5003ec5b7eb2a0102a2f85cecb21fa9512d790139ecc45b6d03f4";
    };
    vorbis = {
      url = "https://github.com/xiph/vorbis/releases/download/v1.3.7/libvorbis-1.3.7.zip";
      sha512 = "10edd193f44f2b2d6085672e257b5be11066f5db27348d4cab53789bf9e8739c2df2cd7f42b83e4edbab53e10b5dc84320d6aab1deac0d8e18196a8a88b19b77";
    };
    freetype = {
      url = "https://github.com/freetype/freetype/archive/VER-2-14-3.zip";
      sha512 = "460ea4dc9cc879822556d801341a1cf3efcd57a13cd4da64169603ea98873337dd19e3c8c6d9054b27d10acbbaa8d5c59b7f560c697b98dc2640bcd88f57554a";
    };
    harfbuzz = {
      url = "https://github.com/harfbuzz/harfbuzz/releases/download/3.2.0/harfbuzz-3.2.0.tar.xz";
      sha512 = "c9d88068d8017046842f444f02f31dbae109026ede943aaf265db5508de8b4b2be84203950f274a237f515bf7cbd361629d2032c6e8ee8f50354b430bba3a8ca";
    };
  };

  # Emscripten treats a port as present when its directory holds the
  # unpacked archive and a .emscripten_url file naming the URL.
  unpackPort = name: port: ''
    mkdir "$out/ports/${name}"
    case "${port.url}" in
      *.zip) unzip -q ${fetchurl port} -d "$out/ports/${name}" ;;
      *) tar -xf ${fetchurl port} -C "$out/ports/${name}" ;;
    esac
    echo "${port.url}" > "$out/ports/${name}/.emscripten_url"
  '';
in
assert lib.assertMsg (emscripten.version == "6.0.9") ''
  emscripten-cache: the port list matches Emscripten 6.0.9, not ${emscripten.version}.
  Update it from tools/ports/*.py of the new version.
'';
stdenvNoCC.mkDerivation {
  pname = "emscripten-cache";
  inherit (emscripten) version;

  dontUnpack = true;
  nativeBuildInputs = [ unzip ];

  installPhase = ''
    cp -r ${emscripten}/share/emscripten/cache $out
    chmod -R u+w $out
    mkdir -p $out/ports
    ${lib.concatStrings (lib.mapAttrsToList unpackPort ports)}
  '';
}
