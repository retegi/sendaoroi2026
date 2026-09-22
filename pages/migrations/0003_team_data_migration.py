from django.db import migrations


def migrate_team_data(apps, schema_editor):
    TeamGroup = apps.get_model("pages", "TeamGroup")
    TeamMember = apps.get_model("pages", "TeamMember")
    TeamMembership = apps.get_model("pages", "TeamMembership")
    CollaboratingEntity = apps.get_model("pages", "CollaboratingEntity")

    def make_member(first_name, last_name_1, last_name_2="", role_es="", role_eu="", description_es="", description_eu="", photo="", is_active=True):
        member, created = TeamMember.objects.get_or_create(
            first_name=first_name,
            last_name_1=last_name_1,
            last_name_2=last_name_2,
            defaults={
                "professional_role_es": role_es,
                "professional_role_eu": role_eu,
                "description_es": description_es,
                "description_eu": description_eu,
                "photo": photo,
                "is_active": is_active,
            },
        )
        if not created:
            member.professional_role_es = member.professional_role_es or role_es
            member.professional_role_eu = member.professional_role_eu or role_eu
            member.description_es = member.description_es or description_es
            member.description_eu = member.description_eu or description_eu
            if member.photo in [None, ""] and photo:
                member.photo = photo
            member.is_active = member.is_active or is_active
            member.save()
        return member

    group_working, _ = TeamGroup.objects.get_or_create(
        name_es="Grupo de trabajo del programa",
        defaults={
            "name_eu": "Programa lan taldea",
            "description_es": "Equipo de coordinación y acompañamiento del programa.",
            "description_eu": "Programa laguntzeko koordinazio eta laguntza taldea.",
            "order": 1,
            "is_active": True,
        },
    )
    group_psychologists, _ = TeamGroup.objects.get_or_create(
        name_es="Grupo de psicólogas",
        defaults={
            "name_eu": "Psikologak",
            "description_es": "Colaboración profesional de psicólogas y terapeutas.",
            "description_eu": "Psikologo eta terapeuta profesionalen lankidetza.",
            "order": 2,
            "is_active": True,
        },
    )
    group_collaborators, _ = TeamGroup.objects.get_or_create(
        name_es="Personas colaboradoras",
        defaults={
            "name_eu": "Lankide kolaboratzaileak",
            "description_es": "Personas colaboradoras en la red de acompañamiento.",
            "description_eu": "Akompanamendu sarea osatzen duten lankide kolaboratzaileak.",
            "order": 3,
            "is_active": True,
        },
    )

    members = [
        (
            "Pili",
            "Zabala",
            "Artano",
            "Vicepresidenta de Berridatzi Elkartea",
            "Berridatzi Elkarteko presidenteordea",
            "Hermana de Joxi Zabala. Mi trayectoria se asienta en la búsqueda incansable de memoria, verdad y justicia, una historia personal que me ha vinculado para siempre con la defensa de los Derechos Humanos. Es precisamente esa mirada, desde la imaginación moral, la que hoy me permite soñar con una comunidad de solidaridad real donde sanar los vínculos que la violencia fragmentó. Sendaoroi se articula como ese deseo de abrir espacios compartidos de diálogo y confianza; estoy convencida de que solo cuidando de esas heridas podemos asentar, de verdad, las bases de la no repetición.",
            "Joxi Zabala ahizpa naiz. Nire ibilbidea memoria, egi eta justiziaren bila etengabean oinarritzen da, giza eskubideen defendatzaile gisa betiko lotuta utzi zidan historia pertsonal bat. Begirada hori, imaginazio moraletik abiatuta, gaur egun errealitateko elkartasun-komunitate bat amets egiteko aukera ematen dit: bortizkeriak zatituta utzitako loturak sendatu. Sendaoroi hori da, elkarrizketa eta konfiantzako espazio partekatuak irekitzeko nahia; sinetsita nago zauri horiek zaintzen ez baditugu, ezin direla benetan ezarri no repetición edo errepikapenaren oinarriak.",
            "img/pili_zabala_artano.png",
            True,
        ),
        (
            "Jesús Mari",
            "Garate",
            "Urruzola",
            "Secretario y tesorero de Berridatzi Elkartea",
            "Berridatzi Elkarteko idazkari eta diruzaina",
            "Máster en Memoria Social y Derechos Humanos. Sendaoroi nació como mi TFM, pero hoy es un proyecto colectivo para atender las hendiduras que la violencia ha dejado en nuestra tierra. No hay técnicas mágicas para sanar esta erosión; solo el compromiso de estar presentes y cuidar, abriendo surcos con paciencia para que la vida poco a poco vuelva a florecer.",
            "Memoria Sozial eta Giza Eskubideen masterra. Sendaoroi nire TFM gisa sortu zen, baina gaur egun proiektu kolektibo bat da, bortizkeriak gure lurraldean utzitako zuloak atzeman eta zaintzeko. Ez dago sendatzeko teknika magikorik; soilik presente egoteko eta zaintzeko konpromisoa, arretaz zuloak zabalduz, bizitza pixkanaka berriro loratzen joan dadin.",
            "img/jesus_mari_garate.png",
            True,
        ),
        (
            "Aitziber",
            "Blanco",
            "Goikoetxea",
            "Miembro del grupo de trabajo del programa",
            "Programa lan taldeko kidea",
            "Coordinación y facilitación",
            "Koordinazioa eta erraztapena",
            "",
            True,
        ),
        (
            "Mar",
            "Puga",
            "",
            "Acogida y facilitación",
            "Harrera eta erraztapena",
            "Desde hace unos años me dedico a facilitar espacios de diálogo y escucha desde un enfoque restaurativo. Formar parte de este proyecto tiene mucho sentido para mí porque resuena profundamente con mis valores y con mi visión de cómo debemos sostener y acompañar.",
            "Duela urte batzuk, elkarrizketa eta entzunezko espazioak erraztatzen ari naiz ikuspegi errestauratibotik. Proiektu honen parte izateak zentzua du nire balioen eta laguntzaren ikuspegiaren barruan.",
            "",
            True,
        ),
        (
            "Olatz",
            "Barrenetxea",
            "",
            "Psikólogo clínico",
            "Psikologo klinikoa",
            "Psikologo klinikoa, trauma, giza eskubideen urraketak eta indarkeria jaso dituzten pertsonak urte luzez laguntzen ibilitako esperientzia ondoren, Ekimen Elkartea eta Sendaoroi programaren kolaboratzaile gisa.",
            "Psikologo klinikoa, trauma, giza eskubideen urraketak eta indarkeria jaso dituzten pertsonak urte luzez laguntzen ibilitako esperientzia ondoren, Ekimen Elkartea eta Sendaoroi programaren kolaboratzaile gisa.",
            "img/olatz_barrenetxea.png",
            True,
        ),
        (
            "Maritxu",
            "Jimenez",
            "",
            "Psicoterapeuta humanista y psicóloga sanitaria",
            "Psikoterapeuta humanista eta psikologa sanitarioa",
            "Banakako terapia, bikote terapia eta talde terapia. Sortzen Psikoterapia Humanista Zentroa.",
            "Banakako terapia, bikote terapia eta talde terapia. Sortzen Psikoterapia Humanista Zentroa.",
            "img/maritxu.png",
            True,
        ),
        (
            "Nagore",
            "López de Luzuriaga",
            "",
            "Psicóloga sanitaria. Terapia individual, de pareja y familiar",
            "Psikologa sanitarioa. Banako, bikote eta familia terapia",
            "Giza Eskubideen testuinguruan lan psikosoziala eta klinikoa garatu izan dut urteetan, familiekin esku-hartzean, indarkeria pairatutako banako zein taldeekin lanean, eta baita ikerketa eremuan ere Istanbulgo Protokoloaren peritatzaile gisa.",
            "Giza Eskubideen testuinguruan lan psikosoziala eta klinikoa garatu izan dut urteetan, familiekin esku-hartzean, indarkeria pairatutako banako zein taldeekin lanean, eta baita ikerketa eremuan ere Istanbulgo Protokoloaren peritatzaile gisa.",
            "img/nagore_lopez_de_luzuriaga.png",
            True,
        ),
        (
            "Leire",
            "García",
            "",
            "Psicoterapeuta, colaboradora de Ekimen",
            "Psikoterapeuta, Ekimen-en kolaboratzailea",
            "Leire García, psicoterapeuta. Sendaoroi programaren kolaboratzailea, memoria eta giza eskubideekiko konpromisoaren alde lanean.",
            "Leire García, psikoterapeuta. Sendaoroi programaren kolaboratzailea, memoria eta giza eskubideekiko konpromisoaren alde lanean.",
            "img/leire_garcia.png",
            True,
        ),
        (
            "Uxoa",
            "Larramendi",
            "",
            "Psicoterapeuta, colaboradora de Ekimen",
            "Psikoterapeuta, Ekimen-en kolaboratzailea",
            "Uxoa Larramendi, psicoterapeuta. Sendaoroi programaren kolaboratzailea, gure lana giza eskubideen urraketen eragina jasan dutenei laguntzea da, norbanakoaren eta gizarte osoaren osasun mentalerako memoria eta erreparazioa funtsezkoak direla ulertuta.",
            "Uxoa Larramendi, psikoterapeuta. Sendaoroi programaren kolaboratzailea, gure lana giza eskubideen urraketen eragina jasan dutenei laguntzea da, norbanakoaren eta gizarte osoaren osasun mentalerako memoria eta erreparazioa funtsezkoak direla ulertuta.",
            "img/uxoa_larramendi.png",
            True,
        ),
        (
            "Myriam",
            "Ruiz",
            "González",
            "Psicóloga sanitaria y terapeuta ocupacional",
            "Psikologa sanitarioa eta terapia okupazionala",
            "Mi interés por la defensa de los Derechos Humanos y mi sensibilidad hacia las consecuencias psicológicas que el ejercicio de la violencia causa sobre las personas me llevan a comprometerme con la atención a aquellas que han sufrido directa o indirectamente daños derivados del abuso de poder.",
            "Nire interesa Giza Eskubideen defentsan eta indarkeria praktikatzeak pertsonengan sortzen dituen ondorio psikologikoen sentikortasunak bultzatuta, boterea abusatzeagatik zuzenean edo zeharka kalteak jasan dituzten pertsonei arreta emateko konpromisoa hartzen dut.",
            "img/myriam_ruiz_gonzalez.png",
            True,
        ),
        (
            "Maitane",
            "Ibernia",
            "Belamendia",
            "Psicóloga sanitaria. Terapeuta de movimiento y danza",
            "Osasun eta gizarte psikologoa. Dantza Mugimendu Terapeuta",
            "Forma parte del equipo terapéutico de Ekimen Gunea y colabora en el Programa Sendaoroi con un enfoque integrador, psicocorporal y con perspectiva feminista y de derechos humanos.",
            "Ekimen Gune terapeutikoaren taldekoa da eta Sendaoroi Programan kolaboratzen du ikuspegi integratzaile, psikosomatikoez eta feminista eta giza eskubideen ikuspegiarekin.",
            "img/maitane_ibernia.png",
            True,
        ),
        (
            "Larrun",
            "Barrenetxea",
            "",
            "Psicóloga",
            "Psikologoa",
            "Psikologoa, torturaren ikerketan kolaboratzaile. Giza Ekimen Elkartearekin elkarlanean aritu naiz; horregatik, Sendaoroi programan kolaboratzaile gisa sartu naiz.",
            "Psikologoa, torturaren ikerketan kolaboratzaile. Giza Ekimen Elkartearekin elkarlanean aritu naiz; horregatik, Sendaoroi programan kolaboratzaile gisa sartu naiz.",
            "img/larrun_barrenetxea.png",
            True,
        ),
        (
            "Iñaki",
            "Markez",
            "",
            "Psiquiatra e investigador social",
            "Psikiatra eta gizarte ikertzailea",
            "Colaborador del programa Sendaoroi desde una mirada comprometida con la salud mental, la memoria, los derechos humanos y el acompañamiento a personas afectadas por experiencias de violencia.",
            "Sendaoroi programaren kolaboratzailea da, osasun mentala, memoria, giza eskubideak eta indarkeria esperientziak jasan dituzten pertsonei laguntzearen ikuspegitik konprometituta.",
            "img/inaki_markez2.png",
            True,
        ),
        (
            "Iñaki",
            "Retegi",
            "",
            "Desarrollo web y apoyo tecnológico",
            "Web garapena eta laguntza teknikoa",
            "Mi aportación a Sendaoroi se centra en la parte técnica y el desarrollo web, ayudando a que el proyecto tenga una presencia digital clara, accesible y útil para las personas que puedan necesitarlo.",
            "Nire ekarpena Sendaoroi proiektuan teknika-aldetik eta web garapenean zentratzen da, proiektuak pertsona beharrak asetzeko presentzia digital argi, eskuragarri eta erabilgarria izaten laguntzeko.",
            "img/inaki_retegi.png",
            True,
        ),
    ]

    for first_name, last_name_1, last_name_2, role_es, role_eu, description_es, description_eu, photo_path, is_active in members:
        member = make_member(first_name, last_name_1, last_name_2, role_es, role_eu, description_es, description_eu, photo_path, is_active)
        if first_name in {"Pili", "Jesús Mari", "Aitziber", "Mar"}:
            group = group_working
        elif first_name in {"Olatz", "Maritxu", "Nagore", "Leire", "Uxoa", "Myriam", "Maitane", "Larrun"}:
            group = group_psychologists
        else:
            group = group_collaborators
        TeamMembership.objects.get_or_create(group=group, member=member, defaults={"order": 1, "is_active": True})

    entity_data = [
        ("Ekimen Elkartea", "img/logo-ekimen.jpg", "Entidad colaboradora en el acompañamiento psicológico y comunitario del programa.", "Akompanamendu psikologiko eta komunitarioan elkarlanean aritzen den erakundea.", "https://www.ekimen.eus", 1, True),
    ]
    for name, logo, description_es, description_eu, website, order, is_active in entity_data:
        CollaboratingEntity.objects.get_or_create(
            name=name,
            defaults={
                "logo": logo,
                "description_es": description_es,
                "description_eu": description_eu,
                "website": website,
                "order": order,
                "is_active": is_active,
            },
        )


def reverse_team_data(apps, schema_editor):
    TeamGroup = apps.get_model("pages", "TeamGroup")
    TeamMember = apps.get_model("pages", "TeamMember")
    TeamMembership = apps.get_model("pages", "TeamMembership")
    CollaboratingEntity = apps.get_model("pages", "CollaboratingEntity")

    TeamMembership.objects.all().delete()
    TeamMember.objects.all().delete()
    TeamGroup.objects.all().delete()
    CollaboratingEntity.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0002_collaboratingentity_teamgroup_teammember_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_team_data, reverse_team_data),
    ]
