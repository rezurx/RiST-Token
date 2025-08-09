#!/bin/bash

# Prompt for token details
read -p "Enter the token name (e.g., MyToken): " token_name
read -p "Enter the token symbol (e.g., MTK): " token_symbol
read -p "Enter the initial supply (e.g., 1000000): " initial_supply

# Create a new directory for the token
project_dir="../$token_name"
mkdir -p "$project_dir"

# Copy the template files to the new directory
cp -r ./* "$project_dir/"

# Replace placeholders in the new project
cd "$project_dir"
sed -i "s/new-token/$token_name/g" package.json
sed -i "s/Token Name/$token_name/g" contracts/Token.sol
sed -i "s/TKN/$token_symbol/g" contracts/Token.sol
sed -i "s/1000000/$initial_supply/g" contracts/Token.sol

# Rename the contract file
mv contracts/Token.sol "contracts/$token_name.sol"

# Update the deploy script to use the new contract name
sed -i "s/Token.sol/$token_name.sol/g" scripts/deploy.js

# Initialize a new git repository
git init

# Install dependencies
npm install

echo "New token project created in $project_dir"
