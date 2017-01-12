# -*- coding: utf-8 -*-
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models

from ideascube.forms import UserForm
from ideascube.library.forms import BookForm, BookSpecimenForm


def utf8(s):
    # Hi, MySQL.
    return s.encode('utf-8').decode('utf-8')

# Class created by running inspectdb from the PMB MySQL database.


class Authors(models.Model):
    author_id = models.AutoField(primary_key=True)
    author_type = models.CharField(max_length=2)
    author_name = models.CharField(max_length=255)
    author_rejete = models.CharField(max_length=255)
    author_date = models.CharField(max_length=255)
    author_see = models.IntegerField()
    author_web = models.CharField(max_length=255)
    index_author = models.TextField(blank=True, null=True)
    author_comment = models.TextField(blank=True, null=True)
    author_lieu = models.CharField(max_length=255)
    author_ville = models.CharField(max_length=255)
    author_pays = models.CharField(max_length=255)
    author_subdivision = models.CharField(max_length=255)
    author_numero = models.CharField(max_length=50)
    author_import_denied = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'authors'

    def __str__(self):
        return u' '.join([utf8(self.author_rejete), utf8(self.author_name)])


class Empr(models.Model):
    id_empr = models.AutoField(primary_key=True)
    serial = models.CharField(unique=True, max_length=255, blank=True, null=True, db_column='empr_cb')
    empr_nom = models.CharField(max_length=255)
    empr_prenom = models.CharField(max_length=255)
    empr_adr1 = models.CharField(max_length=255)
    empr_adr2 = models.CharField(max_length=255)
    empr_cp = models.CharField(max_length=10)
    empr_ville = models.CharField(max_length=255)
    empr_pays = models.CharField(max_length=255)
    email = models.CharField(max_length=255, db_column='empr_mail')
    empr_tel1 = models.CharField(max_length=255)
    empr_tel2 = models.CharField(max_length=255)
    empr_prof = models.CharField(max_length=255)
    birth_year = models.IntegerField(db_column='empr_year')
    empr_categ = models.SmallIntegerField()
    empr_codestat = models.SmallIntegerField()
    created_at = models.DateTimeField(db_column='empr_creation')
    empr_modif = models.DateField()
    empr_sexe = models.IntegerField()
    empr_login = models.CharField(max_length=255)
    empr_password = models.CharField(max_length=255)
    empr_digest = models.CharField(max_length=255)
    empr_date_adhesion = models.DateField(blank=True, null=True)
    empr_date_expiration = models.DateField(blank=True, null=True)
    empr_msg = models.TextField(blank=True, null=True)
    empr_lang = models.CharField(max_length=10)
    empr_ldap = models.IntegerField(blank=True, null=True)
    type_abt = models.IntegerField()
    last_loan_date = models.DateField(blank=True, null=True)
    empr_location = models.IntegerField()
    date_fin_blocage = models.DateField()
    total_loans = models.BigIntegerField()
    empr_statut = models.BigIntegerField()
    cle_validation = models.CharField(max_length=255)
    empr_sms = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'empr'

    def __str__(self):
        return self.full_name
        return u'{} {}'.format(utf8(self.empr_prenom), utf8(self.empr_nom))

    @property
    def short_name(self):
        return utf8(self.empr_prenom)

    @property
    def full_name(self):
        return u'{} {}'.format(utf8(self.empr_prenom), utf8(self.empr_nom))

    @property
    def gender(self):
        return ('female' if self.empr_sexe == 2
                else 'male' if self.empr_sexe == 1
                else 'undefined')

    COUNTRY_MAPPING = {
        'c': 'CD',
        'b': 'BI',
        'r': 'RW',
    }

    @property
    def country(self):
        # Some rows are empty…
        nation = self.from_custom_field('nation') or 'b'
        code = nation.lower()[:1]
        return self.COUNTRY_MAPPING.get(code, nation)

    @property
    def city(self):
        return self.from_custom_field('ville_burundais') or ''

    @property
    def camp_address(self):
        return ' '.join(filter(None, [self.empr_adr1, self.empr_adr2]))

    @property
    def id_card_number(self):
        return self.from_custom_field('carte_burundais') or ''

    @property
    def refugee_id(self):
        return self.from_custom_field('carte_refugie') or ''

    @property
    def children_under_12(self):
        return int(self.from_custom_field('nbre_enfant12') or 0)

    @property
    def children_under_18(self):
        return int(self.from_custom_field('nbre_enfant18') or 0)

    @property
    def children_above_18(self):
        return int(self.from_custom_field('nbre_enfant19') or 0)

    SCHOOL_MAPPING = {
        'PRI': 'primary',
        'SEC': 'secondary',
        'PRO': 'professional',
        'SUP': 'college',
    }

    @property
    def school_level(self):
        # (12, 'PRO', 'Formation professionnelle', 3),
        # (12, 'SEC', 'Ecole secondaire', 2),
        # (12, 'PRI', 'Ecole primaire', 1),
        # (12, 'SUP', 'Etudes supérieures', 4),
        # ('primary', _('Primary')),
        # ('secondary', _('Secondary')),
        # ('professional', _('Professional')),
        # ('college', _('Higher education')),
        code = self.from_custom_field('etud')
        return self.SCHOOL_MAPPING.get(code)

    @property
    def camp_entry_date(self):
        return self.from_custom_field('date_camp')

    @property
    def phone(self):
        phone = self.empr_tel1
        if self.empr_tel2:
            phone = '{},{}'.format(phone, self.empr_tel2)
        return phone or ''

    @property
    def is_sent_to_school(self):
        return self.from_custom_field('sco') == 'OUI'

    MARITAL_MAPPING = {
        'MAR': 'couple',
        'CEL': 'single',
        'VEU': 'widowed',
    }

    @property
    def marital_status(self):
        # (10, 'MAR', 'Marié', 1),
        # (10, 'CEL', 'Célibataire', 2),
        # (10, 'VEU', 'Veuf(ve)', 3),
        code = self.from_custom_field('etat_civil')
        return self.MARITAL_MAPPING.get(code)

    @property
    def family_status(self):
        # (10, 'MAR', 'Marié', 1),
        # (10, 'CEL', 'Célibataire', 2),
        # (10, 'VEU', 'Veuf(ve)', 3),
        return self.from_custom_field('sit_famil') or ''

    BOX_MAPPING = {
        'VUB': 'seen_box',
        'ORG': 'partner',
        'BOU': 'word_of_mouth',
        'AFF': 'campaign',
        'AUT': 'other'
    }

    @property
    def box_awareness(self):
        code = self.from_custom_field('box')
        # There are invalid values (like 0).
        return self.BOX_MAPPING.get(code, 'other')

    OCCUPATION_MAPPING = {
        'SAN': 'no_profession',
        'ENS': 'teacher',
        'ELE': 'student',
        'GEN': 'profit_profession',
        'AUT': 'other',
    }

    @property
    def current_occupation(self):
        # (6, 'SAN', 'Sans activité professionnelle', 3),
        # (6, 'ENS', 'Enseignant', 2),
        # (6, 'ELE', 'Élève', 1),
        # (6, 'GEN', 'Activité génératrice de revenus', 4),
        # (6, 'AUT', 'Autre', 5),
        # ('student', _('Student')),
        # ('teacher', _('Teacher')),
        # ('no_profession', _('Without profession')),
        # ('profit_profession', _('Profit profession')),
        # ('other', _('Other')),
        code = self.from_custom_field('occupation')
        return self.OCCUPATION_MAPPING.get(code, 'other')

    ORIGIN_OCCUPATION = {
        'NON': 'Sans activité professionnelle',
        'EVE': 'Élève',
        'NON': 'Sans activité professionnelle',
        'GRI': 'Agriculture',
        'VAG': 'Élevage',
        'COM': 'Petit commerce de biens ou de services',
        'ART': 'Artisan spécialisé',
        'TRA': 'Travaux journaliers',
        'ENS': 'Enseignement',
        'ADM': 'Métiers de l''administration',
    }

    @property
    def country_of_origin_occupation(self):
        # (7, 'NON', 'Sans activité professionnelle', 2),
        # (7, 'EVE', 'Élève', 1),
        # (7, 'NON', 'Sans activité professionnelle', 2),
        # (7, 'GRI', 'Agriculture', 3),
        # (7, 'VAG', 'Élevage', 4),
        # (7, 'COM', 'Petit commerce de biens ou de services', 5),
        # (7, 'ART', 'Artisan spécialisé', 6),
        # (7, 'TRA', 'Travaux journaliers', 7),
        # (7, 'ENS', 'Enseignement', 8),
        # (7, 'ADM', 'Métiers de l''administration', 9),
        code = self.from_custom_field('occupation2')
        return self.ORIGIN_OCCUPATION.get(code, self.empr_prof) 

    LANG_MAPPING = {
        'COP': 'u',
        'ECR': 'w',
        'PAR': 's',
        'LU1': 'r'
    }

    @property
    def fr_level(self):
        # (19, 'COP', 'Compris', 3),
        # (19, 'ECR', 'Ecrit', 2),
        # (19, 'PAR', 'Parlé', 1),
        # (19, 'LU1', 'Lu', 4),
        code = self.from_custom_field('lang_fra')
        return self.LANG_MAPPING.get(code)

    @property
    def sw_level(self):
        code = self.from_custom_field('lang_kisw')
        return self.LANG_MAPPING.get(code)

    @property
    def rn_level(self):
        code = self.from_custom_field('lang_kir')
        return self.LANG_MAPPING.get(code)

    ACTIVITY_MAPPING = {
        'GRO': '1',
        'MUS': '2',
        'ACT': '3',
        'INF': '4',
        'ALP': '5',
        'PAR': '6',
        'ENF': '7',
        'TRE': '3',  # Missing other…
    }

    @property
    def camp_activities(self):
        # (14, 'GRO', 'Comité, groupe de représentation', 1),
        # (14, 'MUS', 'Musique, danse, chant', 2),
        # (14, 'ACT', 'Autres activités culturelles', 3),
        # (14, 'INF', 'Ateliers d''informatique', 4),
        # (14, 'ALP', 'Ateliers d''alphabétisation', 5),
        # (14, 'PAR', 'Groupe de parole', 6),
        # (14, 'ENF', 'Activités pour enfants', 7),
        # (14, 'TRE', 'Autre', 8),
        code = self.from_custom_field('activite_camp')
        return self.ACTIVITY_MAPPING.get(code)

    def from_custom_field(self, name):
        # [{'name': u'carte_refugie'}, {'name': u'carte_burundais'},
        # {'name': u'ville_burundais'}, {'name': u'nation'},
        # {'name': u'activite_camp'}, {'name': u'portable'},
        # {'name': u'internet'}, {'name': u'livre'}, {'name': u'box'},
        # {'name': u'lang_fra'}, {'name': u'lang_kisw'},
        # {'name': u'lang_kir'}, {'name': u'n_progress'}]
        try:
            champ = EmprCustom.objects.using('burundi').filter(name=name).get()
        except EmprCustom.DoesNotExist:
            return None
        code = EmprCustomValues.objects.using('burundi').filter(empr_custom_champ=champ.pk, empr_custom_origine=self.pk).values('empr_custom_small_text')
        if not code:
            return None
        return code[0]['empr_custom_small_text']


class EmprCustom(models.Model):
    # "1";"carte_refugie";"Si réfugié : n° de carte";"text";"small_text";"<OPTIONS FOR=""text"">
    # <SIZE>30</SIZE>
    # <MAXSIZE>150</MAXSIZE>
    # <REPEATABLE>0</REPEATABLE>
    # <ISHTML>0</ISHTML>
    # </OPTIONS> ";"1";"0";"1";"0";"0";"0";"100";"0"

    idchamp = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    titre = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=10)
    datatype = models.CharField(max_length=10)
    options = models.TextField(blank=True, null=True)
    multiple = models.IntegerField()
    obligatoire = models.IntegerField()
    ordre = models.IntegerField(blank=True, null=True)
    search = models.IntegerField()
    export = models.IntegerField()
    exclusion_obligatoire = models.IntegerField()
    pond = models.IntegerField()
    opac_sort = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'empr_custom'


class EmprCustomValues(models.Model):
    # "19";"2177";"ECR";NULL;NULL;NULL;NULL
    empr_custom_champ = models.IntegerField()
    empr_custom_origine = models.IntegerField()
    empr_custom_small_text = models.CharField(max_length=255, blank=True, null=True)
    empr_custom_text = models.TextField(blank=True, null=True)
    empr_custom_integer = models.IntegerField(blank=True, null=True)
    empr_custom_date = models.DateField(blank=True, null=True)
    empr_custom_float = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empr_custom_values'


class Exemplaires(models.Model):
    expl_id = models.AutoField(primary_key=True)
    serial = models.CharField(unique=True, max_length=255, blank=True, null=True, db_column='expl_cb')
    expl_notice = models.IntegerField()
    expl_bulletin = models.IntegerField()
    expl_typdoc = models.IntegerField()
    expl_cote = models.CharField(max_length=255, blank=True, null=True)
    expl_section = models.SmallIntegerField()
    expl_statut = models.SmallIntegerField()
    expl_location = models.SmallIntegerField()
    expl_codestat = models.SmallIntegerField()
    expl_date_depot = models.DateField()
    expl_date_retour = models.DateField()
    expl_note = models.TextField()
    expl_prix = models.CharField(max_length=255)
    expl_owner = models.IntegerField()
    expl_lastempr = models.IntegerField()
    last_loan_date = models.DateField(blank=True, null=True)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField()
    type_antivol = models.IntegerField()
    transfert_location_origine = models.SmallIntegerField()
    transfert_statut_origine = models.SmallIntegerField()
    remarks = models.TextField(blank=True, null=True, db_column='expl_comment')
    expl_nbparts = models.IntegerField()
    expl_retloc = models.SmallIntegerField()
    expl_abt_num = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'exemplaires'

    @classmethod
    def for_notice(cls, notice_id):
        return cls.objects.using('burundi').filter(expl_notice=notice_id)


class Notices(models.Model):
    notice_id = models.AutoField(primary_key=True)
    typdoc = models.CharField(max_length=2)
    title = models.TextField(blank=True, null=True, db_column='tit1')
    tit2 = models.TextField(blank=True, null=True)
    tit3 = models.TextField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True, db_column='tit4')
    tparent_id = models.IntegerField()
    tnvol = models.CharField(max_length=100)
    ed1_id = models.IntegerField()
    ed2_id = models.IntegerField()
    coll_id = models.IntegerField()
    subcoll_id = models.IntegerField()
    year = models.CharField(max_length=50, blank=True, null=True)
    nocoll = models.CharField(max_length=255, blank=True, null=True)
    mention_edition = models.CharField(max_length=255)
    isbn = models.CharField(max_length=50, db_column='code')
    npages = models.CharField(max_length=255, blank=True, null=True)
    ill = models.CharField(max_length=255, blank=True, null=True)
    size = models.CharField(max_length=255, blank=True, null=True)
    accomp = models.CharField(max_length=255, blank=True, null=True)
    n_gen = models.TextField()
    n_contenu = models.TextField()
    summary = models.TextField(db_column='n_resume')
    lien = models.TextField()
    eformat = models.CharField(max_length=255)
    index_l = models.TextField()
    indexint = models.IntegerField()
    index_serie = models.TextField(blank=True, null=True)
    index_matieres = models.TextField()
    niveau_biblio = models.CharField(max_length=1)
    niveau_hierar = models.CharField(max_length=1)
    origine_catalogage = models.IntegerField()
    prix = models.CharField(max_length=255)
    index_n_gen = models.TextField(blank=True, null=True)
    index_n_contenu = models.TextField(blank=True, null=True)
    index_n_resume = models.TextField(blank=True, null=True)
    index_sew = models.TextField(blank=True, null=True)
    index_wew = models.TextField(blank=True, null=True)
    statut = models.IntegerField()
    commentaire_gestion = models.TextField()
    create_date = models.DateTimeField()
    update_date = models.DateTimeField()
    signature = models.CharField(max_length=255)
    thumbnail_url = models.TextField()
    date_parution = models.DateField()
    opac_visible_bulletinage = models.IntegerField()
    indexation_lang = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'notices'

    def __str__(self):
        return utf8(self.title)

    @property
    def authors(self):
        links = Responsability.objects.using('burundi').filter(responsability_notice=self.pk).values('responsability_author')  # noqa
        ids = [link['responsability_author'] for link in links]
        return u', '.join([str(a) for a in Authors.objects.using('burundi').filter(author_id__in=ids)])

    @property
    def serie(self):
        if self.tparent_id:
            return Series.objects.using('burundi').filter(serie_id=self.tparent_id).first().serie_name  # noqa
        return ''

    @property
    def publisher(self):
        if self.ed1_id:
            return Publishers.objects.using('burundi').get(pk=self.ed1_id).ed_name  # noqa
        return ''

    LANG_MAPPING = {
        'fre': 'fr',
        'eng': 'en',
        'swa': 'sw',
        'bam': 'bm',
    }

    @property
    def lang(self):
        qs = NoticesLangues.objects.using('burundi').filter(num_notice=self.pk).values('code_langue')  # noqa
        if qs:
            code = qs[0]['code_langue']
            return self.LANG_MAPPING[code]
        return 'fr'  # Some column have no lang...

    SECTION_MAPPING = {
        u'Espace Numérique': 1,
        u'Livres numériques': 1,
        u'Jeunes - Albums': 2,
        u'Jeunes - Romans': 3,
        u'Jeunes - Documentaires': 4,
        u'Jeunes - BD': 5,
        u'Adultes - Romans': 6,
        u'Adultes - Documentaires': 7,
        u'Adultes - BD': 8,
    }

    @property
    def section(self):
        qs = NoticesFieldsGlobalIndex.objects.using('burundi').filter(id_notice=self.pk, code_champ=90, code_ss_champ=3).values('value')
        if qs:
            return self.SECTION_MAPPING[utf8(qs[0]['value'])]
        return 99


class NoticesFieldsGlobalIndex(models.Model):
    id_notice = models.IntegerField()
    code_champ = models.IntegerField()
    code_ss_champ = models.IntegerField()
    ordre = models.IntegerField()
    value = models.TextField()
    pond = models.IntegerField()
    lang = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'notices_fields_global_index'


class NoticesLangues(models.Model):
    num_notice = models.IntegerField()
    type_langue = models.IntegerField()
    code_langue = models.CharField(max_length=3)
    ordre_langue = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'notices_langues'


class Publishers(models.Model):
    ed_id = models.AutoField(primary_key=True)
    ed_name = models.CharField(max_length=255)
    ed_adr1 = models.CharField(max_length=255)
    ed_adr2 = models.CharField(max_length=255)
    ed_cp = models.CharField(max_length=10)
    ed_ville = models.CharField(max_length=96)
    ed_pays = models.CharField(max_length=96)
    ed_web = models.CharField(max_length=255)
    index_publisher = models.TextField(blank=True, null=True)
    ed_comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publishers'


class Responsability(models.Model):
    responsability_author = models.IntegerField()
    responsability_notice = models.IntegerField()
    responsability_fonction = models.CharField(max_length=4)
    responsability_type = models.IntegerField()
    responsability_ordre = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'responsability'


class Series(models.Model):
    serie_id = models.AutoField(primary_key=True)
    serie_name = models.CharField(max_length=255)
    serie_index = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'series'


class Command(BaseCommand):
    help = ('Batch import for old Burundi servers. '
            'Eg.: python manage.py import_burundi makamba user book --dry-run')

    def add_arguments(self, parser):
        parser.add_argument('box', nargs=1,
                            choices=['musasa', 'bwagiriza', 'kavumu',
                                     'makamba'],
                            help='Box to process.')
        parser.add_argument('action', nargs='*',
                            choices=['user', 'book'],
                            help='Actions to run.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Process data, but do not save in database.')

    def abort(self, msg):
        self.stderr.write(msg)
        sys.exit(1)

    def skip(self, msg, metadata):
            self.stderr.write(u'⚠ Skipping. {}.'.format(msg.decode(self.encoding)))  # noqa
            for key, value in metadata.items():
                value = value.decode(self.encoding) if value else ''
                self.stdout.write(u'- {}: {}'.format(key, value))
            self.stdout.write('-' * 20)

    def handle(self, *args, **options):
        self.dryrun = options['dry_run']
        settings.DATABASES['burundi'] = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': options['box'][0],
            'USER': 'root',
        }
        print('Processing {box} data'.format(**options))
        if 'user' in options['action']:
            for row in Empr.objects.using('burundi').all():
                self.process_user(row)
        if 'book' in options['action']:
            for row in Notices.objects.using('burundi').all():
                self.process_notice(row)

    def process_user(self, empr):
        attrs = ['short_name', 'full_name', 'serial', 'birth_year', 'gender',
                 'country', 'city', 'id_card_number', 'children_under_12',
                 'children_under_18', 'children_above_18', 'school_level',
                 'marital_status', 'box_awareness', 'refugee_id', 'phone',
                 'camp_entry_date', 'current_occupation', 'camp_address',
                 'country_of_origin_occupation', 'is_sent_to_school',
                 'camp_activities', 'fr_level', 'rn_level', 'sw_level',
                 'created_at', 'email']
        data = {attr: getattr(empr, attr) for attr in attrs}
        form = UserForm(data)
        if not form.is_valid():
            print('Not valid!', form.errors)
            print(data)
            sys.exit(1)
        if self.dryrun:
            print(data)
        else:
            user = form.save()
            print(user)

    def process_notice(self, notice):
        attrs = ['title', 'isbn', 'authors', 'serie', 'subtitle', 'summary',
                 'publisher', 'lang', 'section']
        data = {attr: getattr(notice, attr) for attr in attrs}
        form = BookForm(data)
        if not form.is_valid():
            print('Not valid!', form.errors)
            print(data)
            sys.exit(1)
        if self.dryrun:
            print(data)
        else:
            book = form.save()
            print(book)
            exemplaires = Exemplaires.for_notice(notice.notice_id)
            for exemplaire in exemplaires:
                self.process_exemplaire(book, exemplaire)

    def process_exemplaire(self, book, exemplaire):
        attrs = ['serial', 'remarks']
        data = {attr: getattr(exemplaire, attr) for attr in attrs}
        data['book'] = book.pk
        form = BookSpecimenForm(data)
        if not form.is_valid():
            print('Not valid!', form.errors)
            print(data)
            sys.exit(1)
        if self.dryrun:
            print(data)
        else:
            form.save()
