#!/usr/bin/env python3
"""Baixa os posts dos últimos N dias de um perfil do Instagram usando o cookie de sessão.

Uso:
    pip install instaloader
    IG_SESSIONID=... python3 baixar_perfil.py pegueibode --dias 90

O valor de IG_SESSIONID é o cookie "sessionid" do instagram.com no seu navegador.
Configure-o como variável de ambiente (nunca commite o valor).
"""
import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import instaloader


def main():
    p = argparse.ArgumentParser()
    p.add_argument("perfil")
    p.add_argument("--dias", type=int, default=90)
    p.add_argument("--saida", default="posts")
    args = p.parse_args()

    sessionid = os.environ.get("IG_SESSIONID")
    if not sessionid:
        sys.exit("Defina a variável de ambiente IG_SESSIONID com o cookie sessionid do Instagram.")

    L = instaloader.Instaloader(
        dirname_pattern=os.path.join(args.saida, "{target}"),
        download_video_thumbnails=False,
        save_metadata=False,
        compress_json=False,
    )
    L.context._session.cookies.set("sessionid", sessionid, domain=".instagram.com")
    L.context.username = os.environ.get("IG_USERNAME", "session")

    limite = datetime.now(timezone.utc) - timedelta(days=args.dias)
    perfil = instaloader.Profile.from_username(L.context, args.perfil)

    total = 0
    for post in perfil.get_posts():
        data = post.date_utc.replace(tzinfo=timezone.utc)
        if data < limite:
            if post.is_pinned:
                continue  # posts fixados podem ser antigos e vir primeiro
            break
        L.download_post(post, target=args.perfil)
        total += 1
    print(f"{total} posts de @{args.perfil} desde {limite:%Y-%m-%d} salvos em {args.saida}/{args.perfil}")


if __name__ == "__main__":
    main()
