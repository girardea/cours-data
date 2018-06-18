#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Lancement du serveur qui fait tourner l'app complète (le tableau de bord).
"""

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--create-db", help="create database",
                        action="store_true", default=False)
    
    args = parser.parse_args()

    if args.create_db:
        print("--> Creating database")
        