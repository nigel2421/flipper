
{ pkgs, ... }:

let
  # Function to parse requirements.txt and convert to a list of packages
  pythonPackages = ps: with ps; [
    (builtins.fromTOML (builtins.readFile ./requirements.txt))
  ];
in
{
  # This list defines the tools for your development environment.
  packages = [
    (pkgs.python3.withPackages pythonPackages)
    pkgs.postgresql_15 # Specifies the PostgreSQL package
  ];

  # This section defines the background services to run.
  services.postgresql = {
    enable = true;      # This turns the database server on.
    package = pkgs.postgresql_15;

    # This script runs ONCE to set up your database.
    # It creates the user and database that Django will connect to.
    initialScript = pkgs.writeText "init-db" '''
      CREATE ROLE ela_flipbook_user WITH LOGIN PASSWORD 'a_secure_password';
      CREATE DATABASE ela_flipbook_db OWNER ela_flipbook_user;
    ''';
  };

  # You can add commands here to run when your environment starts.
  enterShell = ''
    echo "Nix environment is ready. PostgreSQL service is running."
  '';
}
