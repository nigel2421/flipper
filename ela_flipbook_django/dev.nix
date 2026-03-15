{ pkgs, ... }:

{
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # This list defines the tools for your development environment.
  packages = [
    pkgs.python3
    pkgs.postgresql_15 # Specifies the PostgreSQL package
    pkgs.google-cloud-sdk
  ];


  # This section defines the background services to run.
  services.postgresql = {
    enable = true;      # This turns the database server on.
    package = pkgs.postgresql_15;

    # This script runs ONCE to set up your database.
    # It creates the user and database that Django will connect to.
    initialScript = pkgs.writeText "init-db" ''
      CREATE ROLE ela_flipbook_user WITH LOGIN PASSWORD 'a_secure_password';
      CREATE DATABASE ela_flipbook_db OWNER ela_flipbook_user;
    '';
  };

  # You can add commands here to run when your environment starts.
  # enterShell = ''
  #   echo "Nix environment is ready. PostgreSQL service is running."
  # '';
}
