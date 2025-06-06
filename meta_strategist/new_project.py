""" Entry point for creating a new project directory with a mythological codename.

This script selects an available project codename (optionally from a specific pantheon), creates a new directory
in the "outputs" folder, and populates it with a default configuration and a run script.

Usage:
    python new_project.py
"""
from meta_strategist.gen_new_project import create_new_project

if __name__ == "__main__":
    create_new_project()


