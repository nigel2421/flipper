# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python313Full
  ];

  # Sets environment variables in the workspace
  env = {};

  # Search for packages on NixOS Search and then add them to your environment
  # For example:
  #   packages = [
  #     pkgs.cowsay
  #   ];
  #
  # You can also install packages from specific commits of nixpkgs
  # For example:
  #   packages = [
  #     (pkgs.hello.overrideAttrs (oldAttrs: {
  #       src = pkgs.fetchFromGitHub {
  #         owner = "NixOS";
  #         repo = "nixpkgs";
  #         rev = "a0c37136f8f1760cbe25de92f400cf2779d7122e";
  #         sha256 = "0k14h6x148jwbzz2qad82pgjf12aflh99z39w2a1z3c7j2nm8i3c";
  #       };
  #     }))
  #   ];
  #
  # Or from a path on your local machine:
  #   packages = [
  #     (pkgs.hello.overrideAttrs (oldAttrs: {
  #       src = ./hello-2.12.1;
  #     }))
  #   ];

  # Enable a service
  # For example:
  #   services.postgres.enable = true;
  #
  # To see what services are available, see the NixOS options search
  # For example:
  #   https://search.nixos.org/options?channel=unstable&query=services

  # Enter a shell on startup
  # For example:
  #   startup.shell.command = "cowsay 'Welcome to your workspace'";
  #
  # You can also run a command in the background
  # For example:
  #   startup.command = {
  #     command = "npm install && npm run dev";
  #     workspaceFolder = "my-project"; # optional
  #   }

  # For more advanced use cases, you can use the `idx` module
  # For example, to run a command in a different container:
  #   idx.containers.postgres = {
  #     image = "postgres:15";
  #     startup.command = {
  #       command = "pg_isready -U postgres -h localhost";
  #     };
  #   };
}
