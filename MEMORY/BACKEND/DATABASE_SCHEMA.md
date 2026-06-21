# DATABASE_SCHEMA.md

## Identity

### users

* id
* email
* username
* password_hash
* email_verified
* is_active
* created_at
* updated_at

### profiles

* id
* user_id
* first_name
* last_name
* avatar_url
* target_score
* target_exam_year
* preferred_subjects
* study_hours_per_day
* bio
* created_at
* updated_at

### roles

* id
* name

### permissions

* id
* resource
* action

### user_roles

* user_id
* role_id

### role_permissions

* role_id
* permission_id

### audit_log

* id
* user_id
* event_type
* metadata
* created_at

---

## Content

### subjects

* id (UUID PK)
* name (str, unique, indexed)
* code (str, unique, indexed)
* description (text, nullable)
* is_active (bool, default true)
* created_at (datetime)
* updated_at (datetime)

chapters

topics

questions

answer_options

question_tags

---

## Assessment

tests

test_sections

test_questions

attempts

attempt_answers

---

## Intelligence

performance_snapshots

subject_analytics

chapter_analytics

topic_analytics

weakness_signals

---

## Recovery

mistakes

mistake_occurrences

recovery_missions

mission_tasks

weak_topic_recommendations

---

## Constraints

Never delete attempt_answers.

Refresh tokens stored in Redis only.
