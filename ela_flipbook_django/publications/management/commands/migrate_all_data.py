import sqlite3
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.db import transaction
from django.db.models.signals import post_save
from publications.models import (
    Magazine, Article, Author, Tag, Event, Profile, Contributor, Rating, Comment, CommentReport
)
from publications.signals import create_user_profile
from django.utils.text import slugify

User = get_user_model()

class Command(BaseCommand):
    help = 'Migrates ALL data from hostpinnaclrdb.sqlite3 to the current database'

    def add_arguments(self, parser):
        parser.add_argument('--db', type=str, default='hostpinnaclrdb.sqlite3')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before migration')

    def handle(self, *args, **options):
        db_path = options['db']
        clear_existing = options['clear']
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f"Database {db_path} not found."))
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        self.stdout.write(f"Starting FULL migration from {db_path}...")

        try:
            # Disconnect signal to prevent auto-profile creation
            post_save.disconnect(create_user_profile, sender=User)
            
            with transaction.atomic():
                if clear_existing:
                    self.stdout.write("Clearing existing data...")
                    SocialAccount.objects.all().delete()
                    EmailAddress.objects.all().delete()
                    CommentReport.objects.all().delete()
                    Comment.objects.all().delete()
                    Rating.objects.all().delete()
                    Article.objects.all().delete()
                    Magazine.objects.all().delete()
                    Event.objects.all().delete()
                    Author.objects.all().delete()
                    Tag.objects.all().delete()
                    Profile.objects.all().delete()
                    Contributor.objects.all().delete()
                    User.objects.all().delete()

                # 1. Migrate Users
                self.stdout.write("Migrating Users...")
                cursor.execute("SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined FROM auth_user")
                users = cursor.fetchall()
                for u in users:
                    u_id, u_password, u_last_login, u_is_superuser, u_username, u_first_name, u_last_name, u_email, u_is_staff, u_is_active, u_date_joined = u
                    if not User.objects.filter(id=u_id).exists():
                        User.objects.create(
                            id=u_id, password=u_password, last_login=u_last_login,
                            is_superuser=bool(u_is_superuser), username=u_username,
                            first_name=u_first_name, last_name=u_last_name,
                            email=u_email, is_staff=bool(u_is_staff), is_active=bool(u_is_active),
                            date_joined=u_date_joined
                        )

                # 2. Migrate Tags
                self.stdout.write("Migrating Tags...")
                cursor.execute("SELECT id, name, slug FROM publications_tag")
                for t in cursor.fetchall():
                    t_id, t_name, t_slug = t
                    if not Tag.objects.filter(id=t_id).exists():
                        Tag.objects.create(id=t_id, name=t_name, slug=t_slug)

                # 3. Migrate Authors
                self.stdout.write("Migrating Authors...")
                cursor.execute("SELECT id, name, profile_photo, user_id FROM publications_author")
                for a in cursor.fetchall():
                    a_id, a_name, a_photo, a_user_id = a
                    if not Author.objects.filter(id=a_id).exists():
                        Author.objects.create(id=a_id, name=a_name, profile_photo=a_photo, user_id=a_user_id)

                # 4. Migrate Magazines
                self.stdout.write("Migrating Magazines...")
                cursor.execute("SELECT id, title, cover_image, uploaded_at, excerpt, pdf_file FROM publications_magazine")
                for m in cursor.fetchall():
                    m_id, m_title, m_cover, m_uploaded, m_excerpt, m_pdf = m
                    if not Magazine.objects.filter(id=m_id).exists():
                        Magazine.objects.create(
                            id=m_id, title=m_title, cover_image=m_cover, 
                            uploaded_at=m_uploaded, excerpt=m_excerpt or "", 
                            pdf_file=m_pdf, slug=slugify(m_title)
                        )

                # 5. Migrate Articles
                self.stdout.write("Migrating Articles...")
                cursor.execute("SELECT id, title, cover_image, excerpt, is_featured, is_editors_pick, view_count, uploaded_at, summary, author_id, content FROM publications_article")
                for art in cursor.fetchall():
                    a_id, a_title, a_cover, a_excerpt, a_featured, a_editors, a_views, a_uploaded, a_summary, a_author, a_content = art
                    if not Article.objects.filter(id=a_id).exists():
                        Article.objects.create(
                            id=a_id, title=a_title, cover_image=a_cover, 
                            excerpt=a_excerpt or "", is_featured=bool(a_featured), 
                            is_editors_pick=bool(a_editors), view_count=a_views or 0, 
                            uploaded_at=a_uploaded, summary=a_summary or "", 
                            author_id=a_author, content=a_content or "", 
                            slug=slugify(a_title)
                        )

                # 6. Migrate Article-Tag relationships
                self.stdout.write("Migrating Article-Tag Mappings...")
                cursor.execute("SELECT article_id, tag_id FROM publications_article_tags")
                for mapping in cursor.fetchall():
                    art_id, tag_id = mapping
                    try:
                        art = Article.objects.get(id=art_id)
                        tag = Tag.objects.get(id=tag_id)
                        art.tags.add(tag)
                    except (Article.DoesNotExist, Tag.DoesNotExist):
                        continue

                # 7. Migrate Profiles
                self.stdout.write("Migrating Profiles...")
                cursor.execute("SELECT id, bio, company, industry, job_role, job_title, referral_code, referred_by_id, user_id FROM publications_profile")
                for p in cursor.fetchall():
                    p_id, p_bio, p_company, p_industry, p_role, p_title, p_code, p_referred, p_user_id = p
                    if not Profile.objects.filter(id=p_id).exists() and User.objects.filter(id=p_user_id).exists():
                        Profile.objects.create(
                            id=p_id, user_id=p_user_id, bio=p_bio or "", 
                            company=p_company or "", industry=p_industry or "", 
                            job_role=p_role or "", job_title=p_title or "", 
                            referred_by_id=p_referred
                        )

                # 8. Migrate Events
                self.stdout.write("Migrating Events...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='publications_event'")
                if cursor.fetchone():
                    cursor.execute("SELECT id, title, poster, caption, event_date FROM publications_event")
                    for ev in cursor.fetchall():
                        ev_id, ev_title, ev_poster, ev_caption, ev_date = ev
                        if not Event.objects.filter(id=ev_id).exists():
                            Event.objects.create(
                                id=ev_id, title=ev_title, image=ev_poster, 
                                location=ev_caption or "", date=ev_date, 
                                created_at=ev_date
                            )

                # 9. Migrate Contributors
                self.stdout.write("Migrating Contributors...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='publications_contributor'")
                if cursor.fetchone():
                    cursor.execute("SELECT id, full_name, email, phone_number, country, submission_type, subject, message, attachment, submitted_at, field_or_industry, terms_and_conditions FROM publications_contributor")
                    for c in cursor.fetchall():
                        c_id, c_name, c_email, c_phone, c_country, c_type, c_subject, c_msg, c_file, c_date, c_field, c_terms = c
                        if not Contributor.objects.filter(id=c_id).exists():
                            Contributor.objects.create(
                                id=c_id, full_name=c_name, email=c_email, 
                                phone_number=c_phone or "", country=c_country or "", 
                                field_or_industry=c_field or "",
                                submission_type=c_type or 'general', subject=c_subject, 
                                message=c_msg, attachment=c_file, submitted_at=c_date, 
                                terms_and_conditions=bool(c_terms)
                            )

                # 10. Migrate Ratings
                self.stdout.write("Migrating Ratings...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='publications_rating'")
                if cursor.fetchone():
                    cursor.execute("SELECT id, score, article_id, user_id FROM publications_rating")
                    for r in cursor.fetchall():
                        r_id, r_score, r_art_id, r_user_id = r
                        if not Rating.objects.filter(id=r_id).exists() and Article.objects.filter(id=r_art_id).exists() and User.objects.filter(id=r_user_id).exists():
                            Rating.objects.create(id=r_id, score=r_score, article_id=r_art_id, user_id=r_user_id)

                # 11. Migrate Comments
                self.stdout.write("Migrating Comments...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='publications_comment'")
                if cursor.fetchone():
                    cursor.execute("SELECT id, text, created_at, article_id, user_id, is_reported, report_count, parent_id FROM publications_comment")
                    for com in cursor.fetchall():
                        c_id, c_text, c_created, c_art_id, c_user_id, c_reported, c_count, c_parent = com
                        if not Comment.objects.filter(id=c_id).exists() and Article.objects.filter(id=c_art_id).exists() and User.objects.filter(id=c_user_id).exists():
                            Comment.objects.create(
                                id=c_id, text=c_text, created_at=c_created, article_id=c_art_id, 
                                user_id=c_user_id, is_reported=bool(c_reported), 
                                report_count=c_count or 0, parent_id=c_parent
                            )

                # 12. Migrate Comment Reports
                self.stdout.write("Migrating Comment Reports...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='publications_commentreport'")
                if cursor.fetchone():
                    cursor.execute("SELECT id, reason, created_at, is_resolved, comment_id, reporter_id FROM publications_commentreport")
                    for rep in cursor.fetchall():
                        r_id, r_reason, r_created, r_resolved, r_com_id, r_rep_id = rep
                        if not CommentReport.objects.filter(id=r_id).exists() and Comment.objects.filter(id=r_com_id).exists():
                            CommentReport.objects.create(
                                id=r_id, reason=r_reason or "", created_at=r_created, 
                                is_resolved=bool(r_resolved), comment_id=r_com_id, 
                                reporter_id=r_rep_id
                            )

                # 13. Migrate Comment Likes
                self.stdout.write("Migrating Comment Likes...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='publications_comment_liked_by'")
                if cursor.fetchone():
                    cursor.execute("SELECT comment_id, user_id FROM publications_comment_liked_by")
                    for like in cursor.fetchall():
                        l_com_id, l_user_id = like
                        try:
                            com = Comment.objects.get(id=l_com_id)
                            usr = User.objects.get(id=l_user_id)
                            com.liked_by.add(usr)
                        except (Comment.DoesNotExist, User.DoesNotExist):
                            continue

                # 14. Migrate allauth data
                self.stdout.write("Migrating Social Accounts...")
                cursor.execute('SELECT id, email, verified, "primary", user_id FROM account_emailaddress')
                for e in cursor.fetchall():
                    e_id, e_email, e_verified, e_primary, e_user_id = e
                    if not EmailAddress.objects.filter(id=e_id).exists() and User.objects.filter(id=e_user_id).exists():
                        EmailAddress.objects.create(
                            id=e_id, email=e_email, verified=bool(e_verified), 
                            primary=bool(e_primary), user_id=e_user_id
                        )
                
                cursor.execute('SELECT id, provider, uid, last_login, date_joined, extra_data, user_id FROM socialaccount_socialaccount')
                for s in cursor.fetchall():
                    s_id, s_provider, s_uid, s_last_login, s_date_joined, s_extra, s_user_id = s
                    if not SocialAccount.objects.filter(id=s_id).exists() and User.objects.filter(id=s_user_id).exists():
                        SocialAccount.objects.create(
                            id=s_id, provider=s_provider, uid=s_uid, last_login=s_last_login, 
                            date_joined=s_date_joined, extra_data=s_extra, user_id=s_user_id
                        )

            self.stdout.write(self.style.SUCCESS("Successfully migrated ALL site data!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during migration: {str(e)}"))
            import traceback
            traceback.print_exc()
        finally:
            post_save.connect(create_user_profile, sender=User)
            conn.close()
