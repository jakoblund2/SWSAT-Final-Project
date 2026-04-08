{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  name = "swsat";

  packages = with pkgs; [
    python313
  ];

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH

    # activate the venv automatically if it exists
    if [ -d .venv ]; then
      source .venv/bin/activate
    fi
  '';
}