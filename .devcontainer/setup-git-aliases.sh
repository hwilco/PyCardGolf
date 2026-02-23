#!/bin/bash

echo "Configuring Git aliases..."

# Alias: git agent
# Sets local identity to Antigravity Agent
git config --global alias.agent '!git config --local user.name "Antigravity Agent" && git config --local user.email "agent@antigravity.local" && echo "Identity set to Antigravity Agent"'

# Alias: git me
# Unsets local identity to fallback to global/host defaults
git config --global alias.me '!git config --local --unset user.name; git config --local --unset user.email; echo "Identity reset to host default"'

echo "Git aliases successfully configured!"
