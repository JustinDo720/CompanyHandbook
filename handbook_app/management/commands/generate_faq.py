from django.core.management import BaseCommand
from openai import OpenAI 
from django.conf import settings
from handbook_app.models import Handbook, FAQ
from handbook_app.services.pinecone_services import get_index
from django.core.mail import send_mail

# Helper function to feed OpenAI our prompt
def generate_faq(ai_client, handbook):
    """
        In order to build our context we would need to query all the vectors related to our handbook 
            - Query via namespace 

        Grab the metadata text then transform into string format to feed into prompt 
    """
    # Dirty implementation because index.fetch() requires id which we don't know
    #
    # The idea here is to fetch vectors relalted to a specific namespace
    # https://community.pinecone.io/t/is-there-a-way-to-query-all-the-vectors-and-or-metadata-from-a-namespace/797/7
    dummy_question_vector = [0.0] * 1536
    res = get_index().query(
        vector = dummy_question_vector,
        top_k=10000,
        include_metadata=True,
        namespace=handbook.get_pc_namespace()
    )

    context = "\n\n".join(m['metadata']['text'] for m in res['matches'])
    prompt = f"""
        You are an employee at {handbook.company.company_name}.
        Based on the following handbook content, generate 5 realistic questions 
        employees might ask (do not answer them):

        {context}

        Separate each question with the "|" character. 
        Do not include the "|" character inside any question. 
        Do not add comments, extra whitespaces, or malformed syntax.
    """

    # Using OpenAI LLM to generate a response 
    ai_response = ai_client.chat.completions.create(
        model='gpt-4o',
        messages=[{
            'role': 'user',
            'content': prompt
        }],
        temperature = 0
    )

    handbook_faq = ai_response.choices[0].message.content.split('|')
    for q in handbook_faq:
        faq = FAQ.objects.create(handbook=handbook, question=q.strip())

    

class Command(BaseCommand):
    help = "Generate FQA at midnight"

    def add_arguments(self, parser):
        parser.add_argument('-i', '--handbook_id', type=int, help='Handbook ID to generate 5 FQA')


    def handle(self, *args, **kwargs):
        ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        handbook_id = kwargs.get('handbook_id', None)
        num_generated = 0
        if handbook_id:
            # Generating based on a specific handbook
            specific_handbook = Handbook.objects.get(id=handbook_id)
            generate_faq(ai_client, specific_handbook)
            num_generated += 1
        else:
            # NOT OPTIMAL (works but NOT optimal we just want to check for nullity)
            # # Generating based on handbooks that do not have FAQ 
            # all_handbooks = Handbook.objects.all()
            # for handbook in all_handbooks:
            #     if not handbook.faq_set.count > 0:
            #         # Handbook doesn't have FAQ let's add
            #         pass 
            # We could do faq__isnull because of the related_name
            handbooks_without_faq = Handbook.objects.filter(faq__isnull = True)
            for handbook in handbooks_without_faq:
                generate_faq(ai_client, handbook)
                num_generated += 1
        # Regardless of handbook_id, we want to send an email 
        send_mail(
            subject="FAQ Generation Complete",
            message=f"Generated {num_generated} new questions.\nTotal FAQs: {FAQ.objects.count()}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_RECIPIENT, settings.EMAIL_HOST_USER],
            fail_silently=True,
        )
