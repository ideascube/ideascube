# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


from ideasbox.tests.factories import UserFactory
from ideasbox.blog.models import Content
from ideasbox.blog.tests.factories import ContentFactory
from ideasbox.library.tests.factories import BookSpecimenFactory, BookFactory
from ideasbox.mediacenter.tests.factories import DocumentFactory


class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            msg = ('This does not seem to be a dev project. Aborting. You need'
                   ' to be in DEBUG=True')
            raise CommandError(msg)

        # Create some users.
        staff = UserFactory(short_name='Amelia', serial='123456',
                            password='password', is_staff=True)
        UserFactory(short_name='Amy', password='password')
        UserFactory(short_name='Touria', password='password')

        # Create some blog content.
        text = ('The last voice transmission received on Howland Island from '
                'Earhart indicated she and Noonan were flying along a line of '
                'position (taken from a "sun line" running on 157-337 degrees)'
                ' which Noonan would have calculated and drawn on a chart as '
                'passing through Howland. After all contact was lost with '
                'Howland Island, attempts were made to reach the flyers with '
                'both voice and Morse code transmissions. Operators across the'
                ' Pacific and the United States may have heard signals from '
                'the downed Electra but these were unintelligible or weak')
        ContentFactory(title='1937 world flight', text=text, summary=text,
                       status=Content.PUBLISHED, author=staff,
                       image__from_path='ideasbox/tests/data/amelia-earhart.jpg')
        ContentFactory(title='This is another article with a longer title',
                       text=text, summary=text, status=Content.PUBLISHED,
                       author=staff, image=None)
        title = ('The Untold Story of Thirteen American Women and the Dream '
                 'of Space Flight')
        ContentFactory(title=title, text=text, summary=text,
                       status=Content.PUBLISHED, author=staff,
                       image__from_path='ideasbox/tests/data/plane.jpg')
        ContentFactory(title='This is a draft content', text=text,
                       status=Content.DRAFT, author=staff, image=None)
        ContentFactory(title='This is a deleted content', text=text,
                       status=Content.DELETED, author=staff, image=None)

        # Create some books.
        summary = ("If one chanced to examine the catalogues of Kingsbridge "
                   "College for the past hundred years it would be found that "
                   "in most of them is recorded the name of some dead and "
                   "gone Deering-a name famous in the annals of the South-who "
                   "came up from Louisiana, 'marched through the four long "
                   "happy years of college,' as the old song has it, with an "
                   "arts degree to his credit; or, perchance, marched out at "
                   "the end of one or two of them with nothing to his credit "
                   "at all. Kingsbridge was a tradition in the Deering "
                   "family, southern though it was-a tradition that was "
                   "hardly broken, even when in 1861 Victor Deering and a "
                   "hundred other chivalrous youths threw their text-books "
                   "out of the windows and enlisted in the armies of the "
                   "Confederacy. Victor's father, Basil, too, was in the "
                   "war, and laid down his arms at Appomattox as a "
                   "brigadier-general-brevetted for gallantry on the field of "
                   "action. For a while it seemed that no Deerings would go "
                   "to Kingsbridge, but time at length healed the old "
                   "antagonisms, and when it became a question where young "
                   "Anthony, Victor's boy, should go to[2] college, there was "
                   "no longer any question that Kingsbridge should be the "
                   "place.")
        path = 'ideasbox/tests/data/deering-of-deal.jpg'
        book = BookFactory(title='Deering of Deal', summary=summary,
                           subtitle='The Spirit of the School',
                           authors=u'Latta Griswold', lang='en',
                           cover__from_path=path)
        BookSpecimenFactory(book=book, serial="1234567")
        summary = (u"Le roman raconte les aventures d'un Gascon impécunieux "
                   u"de 18 ans, d'Artagnan, venu à Paris pour faire carrière "
                   u"dans le corps des mousquetaires. Il se lie d'amitié avec "
                   u"Athos, Porthos et Aramis, mousquetaires du roi Louis "
                   u"XIII. Ces quatre hommes vont s'opposer au premier "
                   u"ministre, le cardinal de Richelieu et à ses agents, dont "
                   u"le comte de Rochefort et la belle et mystérieuse Milady "
                   u"de Winter, pour sauver l'honneur de la reine de France "
                   u"Anne d'Autriche.")
        path = 'ideasbox/tests/data/les-trois-mousquetaires.jpg'
        book = BookFactory(title='Les Trois Mousquetaires', summary=summary,
                           authors=u'Alexandre Dumas', lang='fr',
                           cover__from_path=path)
        BookSpecimenFactory(book=book, serial="98765479")
        summary = ("With the title of Sense and Sensibility is connected one "
                   "of those minor problems which delight the cummin-splitters"
                   " of criticism. In the Cecilia of Madame D'Arblay-the "
                   "forerunner, if not the model, of Miss Austen-is a "
                   "sentence which at first sight suggests some relationship "
                   "to the name of the book which, in the present series, "
                   "inaugurated Miss Austen's novels. 'The whole of this "
                   "unfortunate business'-says a certain didactic Dr. Lyster, "
                   "talking in capitals, towards the end of volume three of "
                   "Cecilia-'has been the result of Pride and Prejudice,' and "
                   "looking to the admitted familiarity of Miss Austen with "
                   "Madame D'Arblay's work, it has been concluded that Miss "
                   "Austen borrowed from Cecilia, the title of her second "
                   "novel.")
        path = 'ideasbox/tests/data/sense-and-sensibility.jpg'
        book = BookFactory(title='Sense and Sensibility', summary=summary,
                           authors=u'Jane Austen', lang='en',
                           cover__from_path=path)
        BookSpecimenFactory(book=book, serial="32657324")
        summary = (u"النبي (1923) أشهر كتب جبران كتبه بالإنجليزية وترجم إلى "
                   u"أكثر من خمسين لغة، وهو يعتبر بحق رائعة جبران العالمية، "
                   u"مضمونه اجتماعي، مثالي وتأملي فلسفي، وهو يحوي خلاصة "
                   u"الاراء الجبرانية في الحب والزواج والأولاد والبيوت "
                   u"والثياب والبيع والشراء والحرية والثانون والرحمة والعقاب "
                   u"والدين والأخلاق والحياة والموت واللذة والجمال والكرم "
                   u"والشرائع وغيرها، وقد وردت على لسان نبي سمي المصطفى "
                   u"ورسالة النبي رسالة المتصوف المؤمن بوحدة الوجود، وبأن "
                   u"الروح تتعطش للعودة إلى مصدرها، وبأن الحب جوهر الحياة. "
                   u"وفي كتاب النبي يعبر جبران عن آرائه في الحياة عن طريق "
                   u"معالجته للعلاقات الإنسانية التي تربط الإنسان بالإنسان.")
        path = 'ideasbox/tests/data/the-prophet.jpg'
        book = BookFactory(title=u'النبي (كتاب)', summary=summary,
                           authors=u'جبران خليل جبران', lang='ar',
                           cover__from_path=path)
        BookSpecimenFactory(book=book, serial="3213542")
        title = (u"Déclaration des droits de l'homme et du citoyen "
                 u"du 26 août 1789")
        summary = (u"Les Représentants du Peuple Français, constitués en "
                   u"Assemblée Nationale, considérant que l'ignorance, "
                   u"l'oubli ou le mépris des droits de l'Homme sont les "
                   u"seules causes des malheurs publics et de la corruption "
                   u"des Gouvernements, ont résolu d'exposer, dans une "
                   u"Déclaration solennelle, les droits naturels, "
                   u"inaliénables et sacrés de l'Homme, afin que cette "
                   u"Déclaration, constamment présente à tous les Membres du "
                   u"corps social, leur rappelle sans cesse leurs droits et "
                   u"leurs devoirs ; afin que leurs actes du pouvoir "
                   u"législatif, et ceux du pouvoir exécutif, pouvant être à "
                   u"chaque instant comparés avec le but de toute institution "
                   u"politique, en soient plus respectés ; afin que les "
                   u"réclamations des citoyens, fondées désormais sur des "
                   u"principes simples et incontestables, tournent toujours "
                   u"au maintien de la Constitution et au bonheur de tous.")
        path = 'ideasbox/tests/data/declaration-1789.pdf'
        DocumentFactory(title=title, original__from_path=path, summary=summary)
        path = 'ideasbox/tests/data/amelia-earhart.jpg'
        DocumentFactory(title="Picture of Amelia Earhart",
                        original__from_path=path)
        self.stdout.write('Done.')
