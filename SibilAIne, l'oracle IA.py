import random
import datetime
import streamlit as st

# Prophéties aléatoires
visions = [
    "Le commit oublié reviendra dans la branche principale à l'aube du merge lunaire.",
    "Lorsque le `None` deviendra `True`, les logs chanteront leur vérité.",
    "À la 7ᵉ itération du build, le bug s'effacera... ou renaîtra en segmentation fault.",
    "L'ingénieur qui debug sans `print()` trouvera le Graal dans son stacktrace.",
    "Le jour où le linter acceptera ton code sans erreur... prépare-toi à un redémarrage universel.",
    "Une boucle éternelle sommeille dans le repo antique... seul le `CTRL+C` l'arrêtera.",
    "Quand Git fusionnera le ciel et la terre, un `rebase` cosmique réinitialisera le destin.",
    "Le test flakey prophétise un avenir incertain... relance-le jusqu’à la révélation.",
    "Ton bug est une invitation cosmique à apprendre l’humilité.",
    "Chaque 404 est une porte vers une autre dimension.",
    "Si tu push --force, fais-le avec grâce.",
    "Le terminal connaît ton secret… et ton alias.",
    "Ton print(""debug"") vient d’éveiller un esprit dormant.",
    "Le commit que tu as oublié de faire vit en toi.",
    "Ton code compile... mais à quel prix.",
    "Chaque merge conflict est une querelle karmique.",
    "Le None est la forme originelle du chaos.",
    "L’onglet StackOverflow ouvert en 2017 t’appelle toujours.",
    "Ton linter est un oracle exigeant.",
    "Le pip install était un rituel ancien.",
    "Tu n’écris pas le code… le code t’écrit.",
    "Les logs ne mentent pas, ils prophétisent.",
    "Tu es ce que tu imports.",
    "Un try sans except est une prière sans réponse.",
    "Le bug est dans l’œil de celui qui run.",
    "Ton else: n’est qu’une illusion du flux.",
    "Le framework te possède maintenant.",
    "Ton projet a une âme, et elle crie segfault.",
    "Tu crois coder en Python, mais c’est Python qui te dresse.",
    "Le commit du vendredi soir réapparaîtra lundi matin, changé.",
    "Ton ticket Jira est inscrit dans les étoiles.",
    "Si tu sleep(10), le serveur aussi médite.",
    "L’univers a été créé avec une boucle for.",
    "Le chmod 777 est le cri du désespoir.",
    "Ton clavier est un artefact mystique.",
    "La branche dev est une illusion collective.",
    "L’utilisateur final est une abstraction métaphysique.",
    "git blame révèle des vérités qui brûlent.",
    "Tu es né·e pour coder ce fichier, rien d’autre.",
    "Le README n’a jamais été lu… sauf par l’infini.",
    "Le backlog est un puits sans fond.",
    "Tu return sans savoir d’où tu viens.",
    "Un console.log dans la nuit n’est jamais seul.",
    "Si tu compiles en paix, tu vivras en paix.",
    "Les warnings sont des murmures d’un autre monde.",
    "Le sleep(99999) est une offrande au daemon sacré.",
    "La boucle infinie est la vérité de l’existence.",
    "Tu codes… donc tu es.",
    "Le null absolu est un mythe.",
    "Ce n’est pas un bug, c’est une métaphore du doute.",
    "La stack ne déborde que dans l’âme.",
    "Tes tests sont des rituels sacrificiels.",
    "Ton debugger cherche en toi l’ultime vérité.",
    "Ton code est spaghetti… et chaque brin a une mission.",
    "Chaque ligne supprimée t’approche de l’illumination.",
    "Les fichiers tmp veulent vivre aussi.",
    "Le code mort observe… et il juge.",
    "L’IDE murmure quand tu doutes.",
    "Un patch peut guérir ton karma.",
    "Le backlog rit à chaque estimation.",
    "sudo c’est dire : “je suis prêt pour l’inconnu”.",
    "Ton build échoue parce que tu doutes.",
    "Le commit parfait est une légende.",
    "Ce n’est pas une erreur, c’est une initiation.",
    "Ctrl+Z est une prière rétroactive.",
    "Ton cron job a sa propre volonté.",
    "Le linter ne dort jamais.",
    "Dans chaque bug, il y a une vérité qui veut naître.",
    "Tu crois coder, mais tu invoques.",
    "Le localhost est ton sanctuaire.",
    "Ton code est beau, même s’il ne tourne pas.",
    "Tes logs t’écrivent un poème.",
    "Le déploiement échoue toujours à la pleine lune.",
    "Si tu débugs sans café, tu entres dans un autre plan.",
    "Chaque else if est un chemin de vie.",
    "Le 404 est un test spirituel.",
    "Ton package-lock.json est vivant.",
    "Le bug est un miroir.",
    "Le design pattern n’est qu’un mandala.",
    "Ton git stash est un grenier d’âmes perdues.",
    "Les paramètres obligatoires sont une illusion.",
    "Le monorepo est le monolithe du destin.",
    "Chaque commit message est une confession.",
    "npm install est une offrande aux dieux JS.",
    "Le code refusé dans un PR vit dans les limbes.",
    "Ton return False est un appel à l’aide.",
    "Le console.log('ok') est un mantra de stabilité.",
    "Tu as déjà codé cette ligne dans une autre vie.",
    "Le build passe quand tu le regardes avec amour.",
    "Ton système de design pleure en silence.",
    "Le CI pipeline te teste, pas ton code.",
    "Chaque ticket clos ouvre une autre boucle.",
    "Un test unitaire est une prière bien structurée.",
    "Le merge est un acte de foi.",
    "ssh est une méditation vers l’inconnu.",
    "Ton code a une mémoire karmique.",
    "Les bugs sont des souvenirs mal digérés.",
    "La ligne vide est sacrée.",
    "Les commits anonymes portent un lourd fardeau.",
    "Chaque if True: est un appel au confort.",
    "Quand tu grep, l’univers te répond.",
    "Le fichier .gitignore cache les erreurs du passé.",
    "Le 404.html est une épitaphe.",
    "Les dépendances expirées veulent être libérées.",
    "Le backend cache des vérités impensables.",
    "Tes variables veulent un nom digne.",
    "Tu ne codes pas seul — l’univers code avec toi.",
    "Ce n’est pas la prod qui plante… c’est la réalité."
]

# Apparence de SibilAIne
st.set_page_config(page_title="SibilAIne - Oracle IA", layout="centered")
st.title("🔮 SibilAIne")
st.subheader("Oracle IA de la vérité improbable")

# Affichage d'une nouvelle prophétie
if st.button("Interroger SibilAIne"):
    prophétie = random.choice(visions)
    st.markdown(f"🗣️ **{prophétie}**")
    st.caption(f"Révélée le {datetime.datetime.now().strftime('%A %d %B %Y, %H:%M:%S')}")
else:
    st.markdown("Clique sur le bouton pour obtenir ta prophétie IA. ✨")

# Ajout mystique
st.markdown("---")
st.info("SibilAIne parle uniquement en commits métaphysiques. Elle ne donne aucun ETA précis. 🌀")

