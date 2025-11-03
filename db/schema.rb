# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 2021_02_25_121016) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "_education_level", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name", limit: 50, null: false
  end

  create_table "_period_of_service", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name", limit: 75, null: false
  end

  create_table "_race", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name", limit: 40, null: false
  end

  create_table "_service_branch", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name", limit: 75, null: false
  end

  create_table "_sex", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name", limit: 10, null: false
  end

  create_table "_status", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name", limit: 75, null: false
  end

  create_table "acq_sf_r_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "active_admin_comments", force: :cascade do |t|
    t.string "namespace"
    t.text "body"
    t.string "resource_type"
    t.bigint "resource_id"
    t.string "author_type"
    t.bigint "author_id"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.index ["author_type", "author_id"], name: "index_active_admin_comments_on_author"
    t.index ["namespace"], name: "index_active_admin_comments_on_namespace"
    t.index ["resource_type", "resource_id"], name: "index_active_admin_comments_on_resource"
  end

  create_table "admin_users", force: :cascade do |t|
    t.string "email", default: "", null: false
    t.string "encrypted_password", default: "", null: false
    t.string "reset_password_token"
    t.datetime "reset_password_sent_at"
    t.datetime "remember_created_at"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.index ["email"], name: "index_admin_users_on_email", unique: true
    t.index ["reset_password_token"], name: "index_admin_users_on_reset_password_token", unique: true
  end

  create_table "ahrs", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "frequency"
    t.bigint "reality"
    t.bigint "loudness"
    t.bigint "number_of_voices"
    t.bigint "length"
    t.bigint "attentional_salience"
    t.bigint "distress_level"
    t.string "verified_by", limit: 10
  end

  create_table "asrm", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "audit_c", force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "visit_num"
    t.date "date"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "aware_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.bigint "q13"
    t.bigint "q14"
    t.bigint "q15"
    t.bigint "q16"
    t.bigint "q17"
    t.bigint "q18"
    t.bigint "q19"
    t.bigint "q20"
    t.bigint "q21"
    t.bigint "q22"
    t.bigint "q23"
    t.bigint "q24"
    t.bigint "q25"
    t.bigint "q26"
    t.bigint "q27"
    t.bigint "q28"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "bai", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.integer "q21"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "balance_board", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.bigint "study_id"
    t.integer "agilisway_num"
    t.integer "task_code"
    t.string "task", limit: 20
    t.float "ap"
    t.float "ml"
    t.text "character_finished"
    t.bigint "character_count"
    t.string "paragraph_passes", limit: 20
    t.text "comments"
    t.text "administrator"
    t.text "verified_by"
  end

  create_table "balance_task_key", force: :cascade do |t|
    t.string "task", limit: 20
    t.string "created_by", limit: 20
  end

  create_table "bicro_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.bigint "study_id"
    t.integer "injury_type"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.string "q20", limit: 1
    t.string "q21", limit: 1
    t.string "q22", limit: 1
    t.integer "q23"
    t.integer "q24"
    t.string "q25", limit: 1
    t.string "q26", limit: 1
    t.integer "q27"
    t.integer "q28"
    t.integer "q29"
    t.string "q30", limit: 1
    t.string "q31", limit: 1
    t.string "q32", limit: 1
    t.string "q33", limit: 1
    t.string "q34", limit: 1
    t.string "q35", limit: 1
    t.string "q36", limit: 1
    t.string "q37", limit: 1
    t.string "q38", limit: 1
    t.string "q39", limit: 1
    t.text "administrator"
    t.string "verified_by", limit: 20
  end

  create_table "bicro_scored", id: false, force: :cascade do |t|
    t.bigint "id"
    t.bigint "subject_id"
    t.string "date", limit: 255
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "injury_type"
    t.string "administrator", limit: 255
    t.string "verified_by", limit: 255
    t.bigint "personal_care_sum"
    t.float "personal_care_mean"
    t.float "mobility_sum"
    t.float "mobility_mean"
    t.bigint "self_organization_sum"
    t.float "self_organization_mean"
    t.float "contact_partner_child_sum"
    t.float "contact_partner_child_mean"
    t.float "contact_parents_sibs_sum"
    t.float "contact_parents_sibs_mean"
    t.float "socializing_sum"
    t.float "socializing_mean"
    t.float "productive_employment_sum"
    t.float "productive_employment_mean"
    t.float "psychological_well_being_sum"
    t.float "psychological_well_being_mean"
  end

  create_table "biometrics", force: :cascade do |t|
    t.string "subjectid", limit: 6
    t.string "weight", limit: 6
    t.string "bmi", limit: 6
    t.string "notes", limit: 50
  end

  create_table "bis_bas_raw", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.integer "q21"
    t.integer "q22"
    t.integer "q23"
    t.integer "q24"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "bis_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.bigint "study_id"
    t.decimal "bis_1", precision: 1
    t.decimal "bis_2", precision: 1
    t.decimal "bis_3", precision: 1
    t.decimal "bis_4", precision: 1
    t.decimal "bis_5", precision: 1
    t.decimal "bis_6", precision: 1
    t.decimal "bis_7", precision: 1
    t.decimal "bis_8", precision: 1
    t.decimal "bis_9", precision: 1
    t.decimal "bis_10", precision: 1
    t.decimal "bis_11", precision: 1
    t.decimal "bis_12", precision: 1
    t.decimal "bis_13", precision: 1
    t.decimal "bis_14", precision: 1
    t.decimal "bis_15", precision: 1
    t.decimal "bis_16", precision: 1
    t.decimal "bis_17", precision: 1
    t.decimal "bis_18", precision: 1
    t.decimal "bis_19", precision: 1
    t.decimal "bis_20", precision: 1
    t.decimal "bis_21", precision: 1
    t.decimal "bis_22", precision: 1
    t.decimal "bis_23", precision: 1
    t.decimal "bis_24", precision: 1
    t.decimal "bis_25", precision: 1
    t.decimal "bis_26", precision: 1
    t.decimal "bis_27", precision: 1
    t.decimal "bis_28", precision: 1
    t.decimal "bis_29", precision: 1
    t.decimal "bis_30", precision: 1
    t.text "administrator"
    t.string "verified_by", limit: 20, null: false
  end

  create_table "bis_scored", id: false, force: :cascade do |t|
    t.bigint "id"
    t.bigint "subject_id"
    t.string "date", limit: 255
    t.bigint "visit_num"
    t.bigint "study_id"
    t.string "administrator", limit: 255
    t.string "verified_by", limit: 255
    t.float "attentional"
    t.float "motor_2nd_order"
    t.float "nonplanning"
    t.float "attention"
    t.bigint "cognitive_instability"
    t.float "motor_1st_order"
    t.float "perseverance"
    t.float "self_control"
    t.float "cognitive_complexity"
    t.float "total_score"
  end

  create_table "bis_weekly_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.bigint "study_id"
    t.decimal "bis_1", precision: 1
    t.decimal "bis_2", precision: 1
    t.decimal "bis_3", precision: 1
    t.decimal "bis_4", precision: 1
    t.decimal "bis_5", precision: 1
    t.decimal "bis_6", precision: 1
    t.decimal "bis_7", precision: 1
    t.decimal "bis_8", precision: 1
    t.decimal "bis_9", precision: 1
    t.decimal "bis_10", precision: 1
    t.decimal "bis_11", precision: 1
    t.decimal "bis_12", precision: 1
    t.decimal "bis_13", precision: 1
    t.decimal "bis_14", precision: 1
    t.decimal "bis_15", precision: 1
    t.decimal "bis_16", precision: 1
    t.decimal "bis_17", precision: 1
    t.decimal "bis_18", precision: 1
    t.decimal "bis_19", precision: 1
    t.decimal "bis_20", precision: 1
    t.decimal "bis_21", precision: 1
    t.decimal "bis_22", precision: 1
    t.decimal "bis_23", precision: 1
    t.decimal "bis_24", precision: 1
    t.decimal "bis_25", precision: 1
    t.decimal "bis_26", precision: 1
    t.decimal "bis_27", precision: 1
    t.decimal "bis_28", precision: 1
    t.decimal "bis_29", precision: 1
    t.decimal "bis_30", precision: 1
    t.text "administrator"
    t.string "verified_by", limit: 20, null: false
  end

  create_table "bis_wrongq29", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "admin_num"
    t.bigint "study_id"
    t.decimal "bis_1", precision: 1
    t.decimal "bis_2", precision: 1
    t.decimal "bis_3", precision: 1
    t.decimal "bis_4", precision: 1
    t.decimal "bis_5", precision: 1
    t.decimal "bis_6", precision: 1
    t.decimal "bis_7", precision: 1
    t.decimal "bis_8", precision: 1
    t.decimal "bis_9", precision: 1
    t.decimal "bis_10", precision: 1
    t.decimal "bis_11", precision: 1
    t.decimal "bis_12", precision: 1
    t.decimal "bis_13", precision: 1
    t.decimal "bis_14", precision: 1
    t.decimal "bis_15", precision: 1
    t.decimal "bis_16", precision: 1
    t.decimal "bis_17", precision: 1
    t.decimal "bis_18", precision: 1
    t.decimal "bis_19", precision: 1
    t.decimal "bis_20", precision: 1
    t.decimal "bis_21", precision: 1
    t.decimal "bis_22", precision: 1
    t.decimal "bis_23", precision: 1
    t.decimal "bis_24", precision: 1
    t.decimal "bis_25", precision: 1
    t.decimal "bis_26", precision: 1
    t.decimal "bis_27", precision: 1
    t.decimal "bis_28", precision: 1
    t.decimal "bis_29", precision: 1
    t.decimal "bis_30", precision: 1
    t.string "verified_by", limit: 20, null: false
  end

  create_table "bis_wrongq29_scored", id: false, force: :cascade do |t|
    t.bigint "id"
    t.bigint "subject_id"
    t.string "date", limit: 255
    t.bigint "visit_num"
    t.bigint "admin_num"
    t.bigint "study_id"
    t.bigint "page_link"
    t.string "administrator", limit: 255
    t.string "time_stamp", limit: 255
    t.string "verified_by", limit: 255
    t.float "attentional"
    t.float "motor_2nd_order"
    t.float "nonplanning"
    t.float "attention"
    t.bigint "cognitive_instability"
    t.float "motor_1st_order"
    t.float "perseverance"
    t.float "self_control"
    t.float "cognitive_complexity"
    t.float "total_score"
  end

  create_table "blinding_questionnaire", id: :serial, force: :cascade do |t|
    t.bigint "subject_id"
    t.integer " visit_num"
    t.date "date"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.text "q3"
    t.integer "stimulation"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "brain_hq", id: false, force: :cascade do |t|
    t.integer "subject_id"
    t.integer "study_id"
    t.string "exercise_name", limit: 17
    t.string "functional_area", limit: 12
    t.integer "grid_number"
    t.integer "x_coord"
    t.integer "y_coord"
    t.integer "threshold"
    t.string "threshold_units", limit: 7
    t.decimal "z_score", precision: 11, scale: 9
    t.integer "stars_awarded"
    t.string "local_date", limit: 10
    t.bigint "timestamp"
    t.integer "trials_completed"
    t.string "training_context", limit: 7
    t.string "challenge", limit: 9
    t.integer "raw_block_time"
  end

  create_table "brief_raw", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.bigint "a"
    t.bigint "a_other"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "b"
    t.bigint "b_other"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.string "administrator", limit: 50
    t.string "verified by", limit: 50
  end

  create_table "bsi_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "q1"
    t.integer "q2"
    t.bigint "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.bigint "q13"
    t.bigint "q14"
    t.bigint "q15"
    t.bigint "q16"
    t.bigint "q17"
    t.bigint "q18"
    t.bigint "q19"
    t.bigint "q20"
    t.bigint "q21"
    t.bigint "q22"
    t.bigint "q23"
    t.bigint "q24"
    t.bigint "q25"
    t.bigint "q26"
    t.bigint "q27"
    t.bigint "q28"
    t.bigint "q29"
    t.bigint "q30"
    t.bigint "q31"
    t.bigint "q32"
    t.bigint "q33"
    t.bigint "q34"
    t.bigint "q35"
    t.bigint "q36"
    t.bigint "q37"
    t.bigint "q38"
    t.bigint "q39"
    t.bigint "q40"
    t.bigint "q41"
    t.bigint "q42"
    t.bigint "q43"
    t.bigint "q44"
    t.bigint "q45"
    t.bigint "q46"
    t.bigint "q47"
    t.bigint "q48"
    t.bigint "q49"
    t.bigint "q50"
    t.bigint "q51"
    t.bigint "q52"
    t.bigint "q53"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "bssi", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.integer "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.bigint "q13"
    t.bigint "q14"
    t.bigint "q15"
    t.bigint "q16"
    t.bigint "q17"
    t.bigint "q18"
    t.bigint "q19"
    t.bigint "q20"
    t.bigint "q21"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "caffeine_nicotine_use", force: :cascade do |t|
    t.integer "subject_id", null: false
    t.date "date", null: false
    t.integer "visit_num", null: false
    t.integer "study_id", null: false
    t.integer "q1_coffee"
    t.string "q1_coffee_amount_frequency", limit: 200
    t.integer "q1_tea"
    t.string "q1_tea_amount_frequency", limit: 200
    t.integer "q1_soda"
    t.string "q1_soda_amount_frequency", limit: 200
    t.integer "q1_energy"
    t.string "q1_energy_amount_frequency", limit: 200
    t.integer "q1_other"
    t.string "q1_other_amount_frequency", limit: 200
    t.integer "q1_none"
    t.integer "q2_cigarettes"
    t.string "q2_cigarettes_amount_frequency", limit: 200
    t.integer "q2_vap_ecig"
    t.string "q2_vap_ecig_amount_frequency", limit: 200
    t.integer "q2_chew_oral_spit"
    t.string "q2_chew_oral_spit_amount_frequency", limit: 200
    t.integer "q2_other"
    t.string "q2_other_amount_frequency", limit: 200
    t.integer "q2_none"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "call_log", id: :serial, force: :cascade do |t|
    t.date "date_of_call"
    t.string "first_name", limit: 30, null: false
    t.string "last_name", limit: 30, null: false
    t.text "phone_num", null: false
    t.integer "last4_ssn"
    t.date "date_of_birth"
    t.string "subject_id", limit: 5
    t.string "study", limit: 30, null: false
    t.string "referral_source", limit: 30, null: false
    t.integer "tbi"
    t.date "initial_call_back"
    t.date "initial_screen"
    t.date "second_call_back"
    t.date "third_call_back"
    t.bigint "status"
    t.integer "other_studies"
    t.bigint "not_interested"
    t.string "reason_not_interested", limit: 40
    t.text "comments"
    t.string "managed_by", limit: 30, null: false
    t.string "entered_by", limit: 30, null: false
  end

  create_table "caps_5_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "cenc_bart_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 20
    t.integer "subject_id"
    t.integer "visit_num"
    t.string "DataFile.Basename", limit: 25
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 7
    t.integer "group"
    t.integer "ntrials"
    t.integer "PayTotal(Session)"
    t.bigint "randomseed"
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "date", limit: 20
    t.string "sessionstartdatetimeutc", limit: 16
    t.string "sessiontime", limit: 8
    t.string "studioversion", limit: 10
    t.string "trialtitle", limit: 10
    t.integer "trial"
    t.integer "payperpump"
    t.integer "paypop"
    t.integer "PayTotal[Trial]"
    t.integer "PayTrial(Trial)"
    t.string "practicelist", limit: 1
    t.string "practicelist_cycle", limit: 1
    t.string "practicelist_sample", limit: 1
    t.string "Procedure(Trial)", limit: 9
    t.integer "PumpN(Trial)"
    t.integer "pumpnpop"
    t.string "pumpnpoplist", limit: 2
    t.string "Running(Trial)", limit: 12
    t.string "triallist", limit: 1
    t.string "triallist_cycle", limit: 1
    t.string "triallist_sample", limit: 2
    t.integer "sample"
    t.integer "bartslide_acc"
    t.string "bartslide_cresp", limit: 1
    t.string "bartslide_resp", limit: 1
    t.integer "bartslide_rt"
    t.integer "bartslide_rttime"
    t.integer "PayTrial(Sample)"
    t.string "Procedure(Sample)", limit: 8
    t.integer "PumpN(Sample)"
    t.string "Running(Sample)", limit: 8
    t.integer "size"
    t.integer "steplist"
    t.integer "steplist_cycle"
    t.integer "steplist_sample"
  end

  create_table "cenc_bart_scored", id: false, force: :cascade do |t|
    t.string "id", limit: 10
    t.integer "eprime_id"
    t.integer "subject_id"
    t.integer "visit_num"
    t.string "date", limit: 10
    t.integer "study_id"
    t.integer "trials"
    t.integer "adjusted_pumps"
  end

  create_table "cenc_recruited", id: false, force: :cascade do |t|
    t.string "surname", limit: 10
    t.string "first_name", limit: 20, null: false
    t.string "last_name", limit: 20
    t.string "suffix", limit: 20, null: false
    t.string "street1", limit: 50, null: false
    t.string "street2", limit: 50
    t.string "street3", limit: 50
    t.string "city", limit: 20, null: false
    t.string "state", limit: 20, null: false
    t.string "zip", limit: 20, null: false
    t.string "county", limit: 30
  end

  create_table "cenc_stroop_scored", id: false, force: :cascade do |t|
    t.integer "subject_id"
    t.string "condition", limit: 11
    t.integer "count"
    t.decimal "acc_mean", precision: 3, scale: 2
    t.decimal "rt_mean", precision: 11, scale: 7
    t.decimal "acc_median", precision: 2, scale: 1
    t.decimal "rt_median", precision: 5, scale: 1
    t.decimal "interference_rate", precision: 11, scale: 9
  end

  create_table "cenc_subject_ids", primary_key: "cencsubjectid", id: :bigint, default: 0, force: :cascade do |t|
  end

  create_table "cogstate", force: :cascade do |t|
    t.bigint "subject_id"
    t.integer "byear"
    t.string "hand", limit: 5
    t.string "sex", limit: 6
    t.date "tdate"
    t.time "ttime"
    t.integer "study_id"
    t.string "sessn", limit: 10
    t.string "tcode", limit: 4
    t.integer "gmlidx"
    t.float "mps"
    t.integer "dur"
    t.integer "ter"
    t.integer "ler"
    t.integer "rer"
    t.integer "per"
    t.float "lmn"
    t.float "lsd"
    t.float "acc"
    t.integer "cor"
    t.integer "err"
    t.integer "presnt"
    t.integer "cmv"
    t.integer "rth"
    t.integer "sti"
    t.string "cfo", limit: 10
    t.string "res", limit: 10
    t.string "protocolid", limit: 8
  end

  create_table "contrast_sensitivity", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "study_id"
    t.bigint "#_correct_A"
    t.bigint "contrast_score_a"
    t.bigint "#_correct_B"
    t.bigint "contrast_score_b"
    t.bigint "#_correct_C"
    t.bigint "contrast_score_c"
    t.bigint "#_correct_D"
    t.bigint "contrast_score_d"
    t.bigint "#_correct_E"
    t.bigint "contrast_score_e"
    t.string "eye_recorded", limit: 20
    t.bigint "luminance"
    t.bigint "glare"
    t.string "correction", limit: 20
    t.string "examiner", limit: 30
    t.text "test_comments"
    t.text "raw_data"
    t.string "verified_by", limit: 20
  end

  create_table "d_harmony", force: :cascade do |t|
    t.string "Table Name", limit: 50
    t.bigint "priority"
    t.string "created", limit: 8
    t.string "status", limit: 52
    t.string "description", limit: 122
    t.string "Data Entry Method", limit: 30
    t.text "coding", null: false
    t.text "comments"
  end

  create_table "dass", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "q1a"
    t.integer "q1b"
    t.integer "q1c"
    t.integer "q1d"
    t.text "q1_explanation"
    t.integer "q2"
    t.text "q2_explanation"
    t.bigint "q3"
    t.text "q3_explanation"
    t.integer "q4"
    t.text "q4_explanation"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "dass21_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.string "q9", limit: 1
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.string "q14", limit: 1
    t.integer "q15"
    t.string "q16", limit: 1
    t.string "q17", limit: 1
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.string "q21", limit: 1
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "dass21_scored", id: false, force: :cascade do |t|
    t.bigint "id"
    t.bigint "subject_id"
    t.string "date", limit: 255
    t.bigint "visit_num"
    t.bigint "study_id"
    t.string "administrator", limit: 255
    t.string "verified_by", limit: 255
    t.float "depression"
    t.float "anxiety"
    t.float "stress"
  end

  create_table "demographics", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "study_id"
    t.integer "sex"
    t.date "date_of_birth"
    t.integer "race"
    t.integer "status"
    t.integer "service_branch"
    t.integer "period_of_service"
    t.integer "education_level"
    t.string "time_stamp", limit: 30, null: false
    t.text "administrator"
    t.string "verified_by", limit: 10
  end

  create_table "eprime_id", force: :cascade do |t|
    t.bigint "subject_id", null: false
    t.bigint "study_id"
    t.bigint "eprime_id", null: false
    t.text "comments", null: false
    t.string "created_by", limit: 20
  end

  create_table "esi_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "visit_number"
    t.date "date"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.bigint "q13"
    t.bigint "q14"
    t.bigint "q15"
    t.bigint "q16"
    t.bigint "q17"
    t.bigint "q18"
    t.bigint "q19"
    t.bigint "q20"
    t.bigint "q21"
    t.bigint "q22"
    t.bigint "q23"
    t.bigint "q24"
    t.bigint "q25"
    t.bigint "q26"
    t.bigint "q27"
    t.bigint "q28"
    t.bigint "q29"
    t.bigint "q30"
    t.bigint "q31"
    t.bigint "q32"
    t.bigint "q33"
    t.bigint "q34"
    t.bigint "q35"
    t.bigint "q36"
    t.bigint "q37"
    t.bigint "q38"
    t.bigint "q39"
    t.bigint "q40"
    t.bigint "q41"
    t.bigint "q42"
    t.bigint "q43"
    t.bigint "q44"
    t.bigint "q45"
    t.bigint "q46"
    t.bigint "q47"
    t.bigint "q48"
    t.bigint "q49"
    t.bigint "q50"
    t.bigint "q51"
    t.bigint "q52"
    t.bigint "q53"
    t.bigint "q54"
    t.bigint "q55"
    t.bigint "q56"
    t.bigint "q57"
    t.bigint "q58"
    t.bigint "q59"
    t.bigint "q60"
    t.bigint "q61"
    t.bigint "q62"
    t.bigint "q63"
    t.bigint "q64"
    t.bigint "q65"
    t.bigint "q66"
    t.bigint "q67"
    t.bigint "q68"
    t.bigint "q69"
    t.bigint "q70"
    t.bigint "q71"
    t.bigint "q72"
    t.bigint "q73"
    t.bigint "q74"
    t.bigint "q75"
    t.bigint "q76"
    t.bigint "q77"
    t.bigint "q78"
    t.bigint "q79"
    t.bigint "q80"
    t.bigint "q81"
    t.bigint "q82"
    t.bigint "q83"
    t.bigint "q84"
    t.bigint "q85"
    t.text "administrator"
    t.string "verified_by", limit: 35, null: false
  end

  create_table "eye_diagnosis", force: :cascade do |t|
    t.string "diagnosis", limit: 40, null: false
    t.text "description", null: false
    t.integer "ro_neurotrauma", null: false
    t.text "ro_comments", null: false
    t.string "created_by", limit: 20, null: false
  end

  create_table "ftq_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.bigint "q13"
    t.bigint "q14"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "grecc_referrals", force: :cascade do |t|
    t.integer "subject_id", null: false
    t.string "first_name", limit: 15, null: false
    t.string "last_name", limit: 15, null: false
    t.text "phone_num", null: false
    t.integer "last4_ssn", null: false
    t.date "date_of_birth", null: false
    t.integer "referred", null: false
    t.date "date_referred"
    t.integer "enrolled", null: false
    t.text "comments", null: false
    t.string "created_by", limit: 30, null: false
    t.index ["subject_id"], name: "idx_797821_subject_id", unique: true
  end

  create_table "handedness", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "a"
    t.bigint "other_hand_a"
    t.bigint "b"
    t.bigint "other_hand_b"
    t.bigint "c"
    t.bigint "other_hand_c"
    t.bigint "d"
    t.bigint "other_hand_d"
    t.bigint "e"
    t.bigint "other_hand_e"
    t.bigint "f"
    t.bigint "other_hand_f"
    t.bigint "g"
    t.bigint "other_hand_g"
    t.bigint "h"
    t.bigint "other_hand_h"
    t.bigint "i"
    t.bigint "other_hand_i"
    t.bigint "j"
    t.bigint "other_hand_j"
    t.bigint "foot"
    t.bigint "eye"
    t.text "administrator"
    t.string "verified_by", limit: 35
  end

  create_table "headache_nih_examiner_nback", id: false, force: :cascade do |t|
    t.string "task_name", limit: 5
    t.string "task_version", limit: 7
    t.string "task_versiondate", limit: 10
    t.string "task_form", limit: 1
    t.string "task_agecohort", limit: 5
    t.string "task_language", limit: 7
    t.string "site_id", limit: 14
    t.integer "subject_id"
    t.integer "session_num"
    t.string "session_date", limit: 10
    t.string "session_start", limit: 5
    t.string "initials", limit: 3
    t.string "machine_id", limit: 12
    t.string "response_device", limit: 8
    t.string "block_name", limit: 17
    t.integer "trial_number"
    t.integer "trial_location"
    t.string "trial_similarity", limit: 1
    t.string "trial_corr_resp", limit: 5
    t.string "trial_visual_hemi", limit: 1
    t.string "trial_interference", limit: 1
    t.string "resp_value", limit: 5
    t.integer "resp_corr"
    t.decimal "resp_rt", precision: 8, scale: 7
    t.decimal "task_time", precision: 10, scale: 7
  end

  create_table "headache_nih_examiner_nback_summary", id: false, force: :cascade do |t|
    t.string "task_name", limit: 5
    t.string "task_version", limit: 7
    t.string "task_versiondate", limit: 10
    t.string "task_form", limit: 1
    t.string "task_agecohort", limit: 5
    t.string "task_language", limit: 7
    t.string "site_id", limit: 14
    t.integer "subject_id"
    t.integer "session_num"
    t.string "session_date", limit: 10
    t.string "session_start", limit: 5
    t.string "initials", limit: 3
    t.string "machine_id", limit: 12
    t.string "response_device", limit: 8
    t.integer "nb1_total_trials"
    t.decimal "nb1_score", precision: 4, scale: 3
    t.decimal "nb1_bias", precision: 4, scale: 3
    t.integer "nb1_corr"
    t.integer "nb1_errors"
    t.decimal "nb1_mean", precision: 5, scale: 4
    t.decimal "nb1_median", precision: 5, scale: 4
    t.decimal "nb1_stdev", precision: 5, scale: 4
    t.integer "nb1sm_corr"
    t.integer "nb1sm_errors"
    t.decimal "nb1sm_mean", precision: 5, scale: 4
    t.decimal "nb1sm_median", precision: 5, scale: 4
    t.decimal "nb1sm_stdev", precision: 5, scale: 4
    t.integer "nb1s1_corr"
    t.integer "nb1s1_errors"
    t.decimal "nb1s1_mean", precision: 5, scale: 4
    t.decimal "nb1s1_median", precision: 5, scale: 4
    t.decimal "nb1s1_stdev", precision: 5, scale: 4
    t.integer "nb1s2_corr"
    t.integer "nb1s2_errors"
    t.decimal "nb1s2_mean", precision: 5, scale: 4
    t.decimal "nb1s2_median", precision: 5, scale: 4
    t.decimal "nb1s2_stdev", precision: 5, scale: 4
    t.integer "nb1s3_corr"
    t.integer "nb1s3_errors"
    t.decimal "nb1s3_mean", precision: 5, scale: 4
    t.decimal "nb1s3_median", precision: 5, scale: 4
    t.decimal "nb1s3_stdev", precision: 5, scale: 4
    t.integer "nb1s4_corr"
    t.integer "nb1s4_errors"
    t.decimal "nb1s4_mean", precision: 5, scale: 4
    t.decimal "nb1s4_median", precision: 5, scale: 4
    t.decimal "nb1s4_stdev", precision: 5, scale: 4
    t.integer "nb1vhl_corr"
    t.integer "nb1vhl_errors"
    t.decimal "nb1vhl_mean", precision: 5, scale: 4
    t.decimal "nb1vhl_median", precision: 5, scale: 4
    t.decimal "nb1vhl_stdev", precision: 5, scale: 4
    t.integer "nb1vhr_corr"
    t.integer "nb1vhr_errors"
    t.decimal "nb1vhr_mean", precision: 5, scale: 4
    t.decimal "nb1vhr_median", precision: 5, scale: 4
    t.decimal "nb1vhr_stdev", precision: 5, scale: 4
    t.integer "nb2_total_trials"
    t.decimal "nb2_score", precision: 4, scale: 3
    t.decimal "nb2_bias", precision: 4, scale: 3
    t.integer "nb2_corr"
    t.integer "nb2_errors"
    t.decimal "nb2_mean", precision: 5, scale: 4
    t.decimal "nb2_median", precision: 5, scale: 4
    t.decimal "nb2_stdev", precision: 4, scale: 3
    t.integer "nb2sm_corr"
    t.integer "nb2sm_errors"
    t.decimal "nb2sm_mean", precision: 5, scale: 4
    t.decimal "nb2sm_median", precision: 5, scale: 4
    t.decimal "nb2sm_stdev", precision: 4, scale: 3
    t.integer "nb2s1_corr"
    t.integer "nb2s1_errors"
    t.decimal "nb2s1_mean", precision: 5, scale: 4
    t.decimal "nb2s1_median", precision: 5, scale: 4
    t.decimal "nb2s1_stdev", precision: 5, scale: 4
    t.integer "nb2s2_corr"
    t.integer "nb2s2_errors"
    t.decimal "nb2s2_mean", precision: 5, scale: 4
    t.decimal "nb2s2_median", precision: 5, scale: 4
    t.decimal "nb2s2_stdev", precision: 5, scale: 4
    t.integer "nb2s3_corr"
    t.integer "nb2s3_errors"
    t.decimal "nb2s3_mean", precision: 4, scale: 3
    t.decimal "nb2s3_median", precision: 5, scale: 4
    t.decimal "nb2s3_stdev", precision: 5, scale: 4
    t.integer "nb2s4_corr"
    t.integer "nb2s4_errors"
    t.decimal "nb2s4_mean", precision: 5, scale: 4
    t.decimal "nb2s4_median", precision: 5, scale: 4
    t.decimal "nb2s4_stdev", precision: 5, scale: 4
    t.integer "nb2vhl_corr"
    t.integer "nb2vhl_errors"
    t.decimal "nb2vhl_mean", precision: 5, scale: 4
    t.decimal "nb2vhl_median", precision: 5, scale: 4
    t.decimal "nb2vhl_stdev", precision: 5, scale: 4
    t.integer "nb2vhr_corr"
    t.integer "nb2vhr_errors"
    t.decimal "nb2vhr_mean", precision: 5, scale: 4
    t.decimal "nb2vhr_median", precision: 5, scale: 4
    t.decimal "nb2vhr_stdev", precision: 5, scale: 4
    t.integer "nb2int_corr"
    t.integer "nb2int_errors"
    t.decimal "nb2int_mean", precision: 5, scale: 4
    t.decimal "nb2int_median", precision: 5, scale: 4
    t.decimal "nb2int_stdev", precision: 4, scale: 3
    t.integer "nb2noint_corr"
    t.integer "nb2noint_errors"
    t.decimal "nb2noint_mean", precision: 5, scale: 4
    t.decimal "nb2noint_median", precision: 5, scale: 4
    t.decimal "nb2noint_stdev", precision: 5, scale: 4
  end

  create_table "headache_risk_task_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 14
    t.integer "subject"
    t.integer "session"
    t.string "DataFile.Basename", limit: 23
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 8
    t.integer "group"
    t.integer "randomseed"
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 8
    t.string "studioversion", limit: 10
    t.integer "block"
    t.integer "blocklist"
    t.integer "BlockList.Cycle"
    t.integer "BlockList.Sample"
    t.string "practicemode", limit: 2
    t.string "Procedure[Block]", limit: 9
    t.string "Running[Block]", limit: 9
    t.integer "trial"
    t.integer "blueanswerbox"
    t.string "bluebox", limit: 11
    t.string "box1", limit: 15
    t.string "box2", limit: 15
    t.string "box3", limit: 15
    t.string "box4", limit: 15
    t.string "box5", limit: 15
    t.string "box6", limit: 11
    t.string "boxratio", limit: 9
    t.integer "correctanswer"
    t.integer "l"
    t.integer "picturelist"
    t.string "Procedure[Trial]", limit: 9
    t.integer "redanswerbox"
    t.string "redbox", limit: 15
    t.string "Running[Trial]", limit: 9
    t.integer "Slide1.ACC"
    t.integer "Slide1.CRESP"
    t.integer "Slide1.FinishTime"
    t.integer "Slide1.RESP"
    t.integer "Slide1.RT"
    t.integer "Slide1.StartTime"
    t.integer "startvalue"
    t.string "token", limit: 15
    t.string "tokenbox1", limit: 15
    t.string "tokenbox2", limit: 15
    t.string "tokenbox3", limit: 15
    t.string "tokenbox4", limit: 15
    t.string "tokenbox5", limit: 15
    t.string "tokenbox6", limit: 15
    t.integer "totalsum"
    t.integer "trialcount"
    t.integer "triallist"
    t.integer "TrialList.Cycle"
    t.integer "TrialList.Sample"
    t.integer "var"
    t.integer "w"
  end

  create_table "hit6_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "q1"
    t.integer "q2"
    t.bigint "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "hit6_scored", id: false, force: :cascade do |t|
    t.bigint "id"
    t.bigint "subject_id"
    t.string "date", limit: 255
    t.bigint "visit_num"
    t.bigint "study_id"
    t.string "administrator", limit: 255
    t.string "verified_by", limit: 255
    t.float "total_score"
  end

  create_table "hitt_rebion_raw", id: false, force: :cascade do |t|
    t.integer "subject_id"
    t.integer "date"
    t.string "left_at_1", limit: 4
    t.string "left_away_1", limit: 4
    t.string "right_at_1", limit: 4
    t.string "right_away_1", limit: 4
    t.string "left_at_2", limit: 4
    t.string "left_away_2", limit: 4
    t.string "right_at_2", limit: 4
    t.string "right_away_2", limit: 4
    t.string "left_at_3", limit: 4
    t.string "left_away_3", limit: 4
    t.string "right_at_3", limit: 4
    t.string "right_away_3", limit: 4
    t.string "left_at_4", limit: 4
    t.string "left_away_4", limit: 3
    t.string "right_at_4", limit: 4
    t.string "right_away_4", limit: 4
    t.string "left_at_5", limit: 10
    t.string "left_away_5", limit: 10
    t.string "right_at_5", limit: 4
    t.string "right_away_5", limit: 10
    t.decimal "binoc_1", precision: 10, scale: 9
    t.decimal "binoc_2", precision: 10, scale: 9
    t.decimal "binoc_3", precision: 10, scale: 9
    t.decimal "binoc_4", precision: 10, scale: 9
    t.string "binoc_5", limit: 10
    t.decimal "left_fix_1", precision: 10, scale: 9
    t.decimal "left_fix_2", precision: 10, scale: 9
    t.decimal "left_fix_3", precision: 10, scale: 9
    t.decimal "left_fix_4", precision: 10, scale: 9
    t.string "left_fix_5", limit: 10
    t.decimal "right_fix_1", precision: 10, scale: 9
    t.decimal "right_fix_2", precision: 10, scale: 9
    t.decimal "right_fix_3", precision: 10, scale: 9
    t.decimal "right_fix_4", precision: 10, scale: 9
    t.string "right_fix_5", limit: 10
  end

  create_table "htn_24hr_bp", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "condition"
    t.string "sys_avg", limit: 3
    t.string "sys_std", limit: 5
    t.string "dia_avg", limit: 2
    t.string "dia_std", limit: 5
    t.string "heart_rate_avg", limit: 2
    t.string "heart_rate_std", limit: 5
    t.string "verified_by", limit: 5
  end

  create_table "htn_5_facet_mindfulness", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.integer "q21"
    t.integer "q22"
    t.integer "q23"
    t.integer "q24"
    t.integer "q25"
    t.integer "q26"
    t.integer "q27"
    t.integer "q28"
    t.integer "q29"
    t.integer "q30"
    t.integer "q31"
    t.integer "q32"
    t.integer "q33"
    t.integer "q34"
    t.integer "q35"
    t.integer "q36"
    t.integer "q37"
    t.integer "q38"
    t.integer "q39"
    t.string "administrator", limit: 15
    t.string "verified_by", limit: 5
  end

  create_table "htn_demographics", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "sex"
    t.string "date_of_birth", limit: 10
    t.integer "race"
    t.integer "status"
    t.integer "service_branch"
    t.integer "period_of_service"
    t.integer "education_level"
    t.string "administrator", limit: 16
    t.string "verified_by", limit: 5
  end

  create_table "htn_phq_15", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "a"
    t.integer "b"
    t.integer "c"
    t.string "d", limit: 10
    t.integer "e"
    t.integer "f"
    t.integer "g"
    t.integer "h"
    t.integer "i"
    t.integer "j"
    t.string "k", limit: 1
    t.integer "l"
    t.integer "m"
    t.integer "n"
    t.integer "o"
    t.string "administrator", limit: 15
    t.string "verified_by", limit: 5
  end

  create_table "htn_phq_9", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.string "qdifficulty", limit: 1
    t.string "administrator", limit: 15
    t.string "verified_by", limit: 5
  end

  create_table "htn_subjects", force: :cascade do |t|
    t.integer "subject_id"
    t.string "first_name", limit: 8
    t.string "last_name", limit: 12
    t.integer "age"
    t.integer "group"
    t.string "verified_by", limit: 5
  end

  create_table "htn_subjects_group", force: :cascade do |t|
    t.integer "subject_id", null: false
    t.string "group", limit: 10, null: false
    t.string "administrator", limit: 10, null: false
  end

  create_table "htn_whoqol_bref", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "gender"
    t.integer "age"
    t.string "primary_reason_services", limit: 1
    t.integer "race"
    t.string "ethnicity", limit: 1
    t.integer "length_of_service"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.integer "q21"
    t.integer "q22"
    t.integer "q23"
    t.integer "q24"
    t.integer "q25"
    t.integer "q26"
    t.integer "q27"
    t.string "administrator", limit: 15
    t.string "verified_by", limit: 5
  end

  create_table "idas_64_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "visit_number"
    t.date "date"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.bigint "q13"
    t.bigint "q14"
    t.bigint "q15"
    t.bigint "q16"
    t.bigint "q17"
    t.bigint "q18"
    t.bigint "q19"
    t.bigint "q20"
    t.bigint "q21"
    t.bigint "q22"
    t.bigint "q23"
    t.bigint "q24"
    t.bigint "q25"
    t.bigint "q26"
    t.bigint "q27"
    t.bigint "q28"
    t.bigint "q29"
    t.bigint "q30"
    t.bigint "q31"
    t.bigint "q32"
    t.bigint "q33"
    t.bigint "q34"
    t.bigint "q35"
    t.bigint "q36"
    t.bigint "q37"
    t.bigint "q38"
    t.bigint "q39"
    t.bigint "q40"
    t.bigint "q41"
    t.bigint "q42"
    t.bigint "q43"
    t.bigint "q44"
    t.bigint "q45"
    t.bigint "q46"
    t.bigint "q47"
    t.bigint "q48"
    t.bigint "q49"
    t.bigint "q50"
    t.bigint "q51"
    t.bigint "q52"
    t.bigint "q53"
    t.bigint "q54"
    t.bigint "q55"
    t.bigint "q56"
    t.bigint "q57"
    t.bigint "q58"
    t.bigint "q59"
    t.bigint "q60"
    t.bigint "q61"
    t.bigint "q62"
    t.bigint "q63"
    t.bigint "q64"
    t.text "administrator"
    t.string "verified_by", limit: 30, null: false
  end

  create_table "ids_sr_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "visit_number"
    t.date "date"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q9a"
    t.bigint "q9b"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.bigint "q13"
    t.bigint "q14"
    t.bigint "q15"
    t.bigint "q16"
    t.bigint "q17"
    t.bigint "q18"
    t.bigint "q19"
    t.bigint "q20"
    t.bigint "q21"
    t.bigint "q22"
    t.bigint "q23"
    t.bigint "q24"
    t.bigint "q25"
    t.bigint "q26"
    t.bigint "q27"
    t.bigint "q28"
    t.bigint "q29"
    t.bigint "q30"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "impulsivity_bart_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 255
    t.bigint "subject"
    t.bigint "session"
    t.string "datafilebasename", limit: 255
    t.float "displayrefreshrate"
    t.string "experimentversion", limit: 255
    t.bigint "group"
    t.bigint "ntrials"
    t.bigint "paytotalsession"
    t.bigint "randomseed"
    t.string "runtimecapabilities", limit: 255
    t.string "runtimeversion", limit: 255
    t.string "runtimeversionexpected", limit: 255
    t.string "sessiondate", limit: 255
    t.string "sessionstartdatetimeutc", limit: 255
    t.string "sessiontime", limit: 255
    t.string "studioversion", limit: 255
    t.string "trialtitle", limit: 5
    t.bigint "trial"
    t.bigint "payperpump"
    t.bigint "paypop"
    t.bigint "paytotaltrial"
    t.bigint "paytrialtrial"
    t.bigint "practicelist"
    t.bigint "practicelistcycle"
    t.bigint "practicelistsample"
    t.string "proceduretrial", limit: 255
    t.bigint "pumpntrial"
    t.bigint "pumpnpop"
    t.bigint "pumpnpoplist"
    t.string "runningtrial", limit: 255
    t.bigint "triallist"
    t.bigint "triallistcycle"
    t.bigint "triallistsample"
    t.bigint "sample"
    t.bigint "bartslideacc"
    t.string "bartslidecresp", limit: 255
    t.string "bartslideresp", limit: 255
    t.bigint "bartslidert"
    t.bigint "bartsliderttime"
    t.bigint "paytrialsample"
    t.string "proceduresample", limit: 255
    t.bigint "pumpnsample"
    t.string "runningsample", limit: 255
    t.bigint "size"
    t.bigint "steplist"
    t.bigint "steplistcycle"
    t.bigint "steplistsample"
  end

  create_table "impulsivity_bart_scored", id: false, force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "study_id"
    t.float "eprime_id"
    t.float "session"
    t.string "date", limit: 255
    t.float "trials"
    t.float "adjusted_pumps"
    t.float "points_earned"
    t.float "reaction_time_mean"
  end

  create_table "impulsivity_cued_reaching_task", id: false, force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "session"
    t.bigint "error_code"
    t.bigint "range_of_cue"
    t.bigint "cue_trigger_code"
    t.bigint "target_trigger_code"
    t.float "reaction_time"
    t.float "movement_time"
    t.bigint "cue_position_deg"
    t.bigint "target_position_deg"
  end

  create_table "impulsivity_delay_discounting_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 22
    t.integer "subject"
    t.integer "session"
    t.integer "age"
    t.string "DataFile.Basename", limit: 29
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 8
    t.string "group", limit: 4
    t.bigint "randomseed"
    t.string "runtimecapabilities", limit: 12
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 7
    t.string "studioversion", limit: 10
    t.integer "block"
    t.string "Condition[Block]", limit: 11
    t.string "experimentlist", limit: 1
    t.string "ExperimentList.Cycle", limit: 1
    t.string "ExperimentList.Sample", limit: 1
    t.string "increment", limit: 2
    t.string "initialpracticelist", limit: 1
    t.string "InitialPracticeList.Cycle", limit: 1
    t.string "InitialPracticeList.Sample", limit: 1
    t.string "introlist", limit: 1
    t.string "IntroList.Cycle", limit: 1
    t.string "IntroList.Sample", limit: 1
    t.string "MaxBottom[Block]", limit: 1
    t.string "MaxTop[Block]", limit: 4
    t.string "MinBottom[Block]", limit: 1
    t.string "MinTop[Block]", limit: 4
    t.string "PracticeSlide.ACC", limit: 1
    t.string "PracticeSlide.CRESP", limit: 10
    t.string "PracticeSlide.RESP", limit: 1
    t.string "PracticeSlide.RT", limit: 4
    t.string "PracticeSlide.RTTime", limit: 6
    t.string "Procedure[Block]", limit: 14
    t.string "Running[Block]", limit: 19
    t.string "secondpracticelist", limit: 1
    t.string "SecondPracticeList.Cycle", limit: 1
    t.string "SecondPracticeList.Sample", limit: 1
    t.string "standard", limit: 7
    t.string "strFirstChoice[Block]", limit: 14
    t.string "strSecondChoice[Block]", limit: 24
    t.string "validchoice", limit: 8
    t.string "Value[Block]", limit: 3
    t.string "VariableAmount[Block]", limit: 7
    t.string "waittime", limit: 2
    t.string "trial", limit: 1
    t.string "Condition[Trial]", limit: 5
    t.string "condlist", limit: 1
    t.string "CondList.Cycle", limit: 1
    t.string "CondList.Sample", limit: 1
    t.string "Procedure[Trial]", limit: 8
    t.string "Running[Trial]", limit: 8
    t.string "Value[Trial]", limit: 1
    t.string "subtrial", limit: 3
    t.string "firstblocklist", limit: 1
    t.string "FirstBlockList.Cycle", limit: 1
    t.string "FirstBlockList.Sample", limit: 2
    t.string "Procedure[SubTrial]", limit: 14
    t.string "Running[SubTrial]", limit: 15
    t.string "secondblocklist", limit: 1
    t.string "SecondBlockList.Cycle", limit: 2
    t.string "SecondBlockList.Sample", limit: 2
    t.string "loglevel5", limit: 1
    t.string "adjustedmaxbottom", limit: 8
    t.string "adjustedmaxtop", limit: 10
    t.string "adjustedminbottom", limit: 8
    t.string "adjustedmintop", limit: 10
    t.string "choice", limit: 8
    t.string "ChoiceSlide.ACC", limit: 1
    t.string "ChoiceSlide.CRESP", limit: 10
    t.string "ChoiceSlide.RESP", limit: 1
    t.string "ChoiceSlide.RT", limit: 5
    t.string "ChoiceSlide.RTTime", limit: 6
    t.string "Condition[LogLevel5]", limit: 11
    t.string "condnum", limit: 2
    t.string "difference", limit: 5
    t.string "MaxBottom[LogLevel5]", limit: 8
    t.string "MaxTop[LogLevel5]", limit: 10
    t.string "MinBottom[LogLevel5]", limit: 8
    t.string "MinTop[LogLevel5]", limit: 10
    t.string "newtriallist", limit: 1
    t.string "NewTrialList.Cycle", limit: 2
    t.string "NewTrialList.Sample", limit: 2
    t.string "Procedure[LogLevel5]", limit: 15
    t.string "randomlist", limit: 1
    t.string "RandomList.Cycle", limit: 2
    t.string "RandomList.Sample", limit: 2
    t.string "Running[LogLevel5]", limit: 12
    t.string "strFirstChoice[LogLevel5]", limit: 24
    t.string "strSecondChoice[LogLevel5]", limit: 24
    t.string "triallist", limit: 1
    t.string "TrialList.Cycle", limit: 3
    t.string "TrialList.Sample", limit: 2
    t.string "trialnum", limit: 3
    t.string "Value[LogLevel5]", limit: 3
    t.string "VariableAmount[LogLevel5]", limit: 8
  end

  create_table "impulsivity_letters_sent", id: false, force: :cascade do |t|
    t.string "first", limit: 11
    t.string "last", limit: 11
    t.string "suffix", limit: 10
    t.string "street_1", limit: 35
    t.string "street_2", limit: 10
    t.string "street_3", limit: 10
    t.string "city", limit: 16
    t.string "state", limit: 2
    t.integer "zip"
  end

  create_table "impulsivity_risk_task_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 14
    t.integer "subject"
    t.integer "session"
    t.string "DataFile.Basename", limit: 21
    t.integer "Display.RefreshRate"
    t.string "experimentversion", limit: 9
    t.integer "group"
    t.bigint "randomseed"
    t.string "runtimecapabilities", limit: 12
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 7
    t.string "studioversion", limit: 10
    t.integer "block"
    t.integer "blocklist"
    t.integer "BlockList.Cycle"
    t.integer "BlockList.Sample"
    t.string "practicemode", limit: 2
    t.string "Procedure[Block]", limit: 9
    t.string "Running[Block]", limit: 9
    t.integer "trial"
    t.integer "blueanswerbox"
    t.string "bluebox", limit: 11
    t.string "box1", limit: 15
    t.string "box2", limit: 15
    t.string "box3", limit: 15
    t.string "box4", limit: 15
    t.string "box5", limit: 15
    t.string "box6", limit: 11
    t.string "boxratio", limit: 9
    t.integer "correctanswer"
    t.integer "l"
    t.integer "picturelist"
    t.string "Procedure[Trial]", limit: 9
    t.integer "redanswerbox"
    t.string "redbox", limit: 15
    t.string "Running[Trial]", limit: 9
    t.integer "Slide1.ACC"
    t.integer "Slide1.CRESP"
    t.integer "Slide1.FinishTime"
    t.integer "Slide1.RESP"
    t.integer "Slide1.RT"
    t.integer "Slide1.StartTime"
    t.integer "startvalue"
    t.string "token", limit: 15
    t.string "tokenbox1", limit: 15
    t.string "tokenbox2", limit: 15
    t.string "tokenbox3", limit: 15
    t.string "tokenbox4", limit: 15
    t.string "tokenbox5", limit: 15
    t.string "tokenbox6", limit: 15
    t.integer "totalsum"
    t.integer "trialcount"
    t.integer "triallist"
    t.integer "TrialList.Cycle"
    t.integer "TrialList.Sample"
    t.integer "var"
    t.integer "w"
  end

  create_table "impulsivity_risk_task_scored", id: false, force: :cascade do |t|
    t.bigint "eprime_id"
    t.bigint "subject_id"
    t.bigint "study_id"
    t.float "session"
    t.string "date", limit: 255
    t.float "lowriskchoice"
    t.float "totalpoints"
  end

  create_table "madrs_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "q1"
    t.integer "q2"
    t.bigint "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "mbias_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "mbias_1"
    t.integer "mbias_2"
    t.integer "mbias_3"
    t.integer "mbias_4"
    t.integer "mbias_5"
    t.integer "mbias_6"
    t.integer "mbias_7"
    t.integer "mbias_8"
    t.bigint "mbias_9"
    t.bigint "mbias_10"
    t.bigint "mbias_11"
    t.bigint "mbias_12"
    t.bigint "mbias_13"
    t.bigint "mbias_14"
    t.bigint "mbias_15"
    t.bigint "mbias_16"
    t.bigint "mbias_17"
    t.bigint "mbias_18"
    t.bigint "mbias_19"
    t.bigint "mbias_20"
    t.bigint "mbias_21"
    t.bigint "mbias_22"
    t.bigint "mbias_23"
    t.bigint "mbias_24"
    t.bigint "mbias_25"
    t.bigint "mbias_26"
    t.bigint "mbias_27"
    t.bigint "mbias_28"
    t.bigint "mbias_29"
    t.bigint "mbias_30"
    t.bigint "mbias_31"
    t.bigint "mbias_32"
    t.bigint "mbias_33"
    t.bigint "mbias_34"
    t.bigint "mbias_35"
    t.bigint "mbias_36"
    t.bigint "mbias_37"
    t.bigint "mbias_38"
    t.bigint "mbias_39"
    t.bigint "mbias_40"
    t.bigint "mbias_41"
    t.bigint "mbias_42"
    t.bigint "mbias_43"
    t.bigint "mbias_44"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 20
  end

  create_table "mbias_scored", id: false, force: :cascade do |t|
    t.bigint "id"
    t.bigint "subject_id"
    t.string "date", limit: 255
    t.bigint "visit_num"
    t.bigint "study_id"
    t.string "administrator", limit: 255
    t.string "verified_by", limit: 255
    t.bigint "nsi_total"
    t.bigint "pcl_total"
    t.bigint "pcl_critb"
    t.bigint "pcl_critc"
    t.bigint "pcl_critd"
    t.bigint "mbias_total"
    t.bigint "validity_10"
  end

  create_table "medication_information", id: :serial, force: :cascade do |t|
    t.text "drug_name", null: false
    t.text "commercial_name", null: false
    t.text "common_use", null: false
    t.text "other_info"
    t.text "created_by", null: false
  end

  create_table "medication_review_hallucinations", force: :cascade do |t|
    t.bigint "subject_id", null: false
    t.date "date"
    t.bigint "study_id"
    t.integer "med_changes"
    t.string "meds_1", limit: 20
    t.string "meds_1_dose", limit: 20
    t.string "meds_2", limit: 20
    t.string "meds_2_dose", limit: 20
    t.string "meds_3", limit: 20
    t.string "meds_3_dose", limit: 20
    t.string "meds_4", limit: 20
    t.string "meds_4_dose", limit: 20
    t.string "meds_5", limit: 20
    t.string "meds_5_dose", limit: 20
    t.string "meds_6", limit: 20
    t.string "meds_6_dose", limit: 20
    t.string "meds_7", limit: 20
    t.string "meds_7_dose", limit: 20
    t.string "meds_8", limit: 20, null: false
    t.string "meds_8_dose", limit: 20
    t.string "meds_9", limit: 20
    t.string "meds_9_dose", limit: 20
    t.string "meds_10", limit: 20
    t.string "meds_10_dose", limit: 20
    t.string "meds_11", limit: 20
    t.string "meds_11_dose", limit: 20
    t.string "meds_12", limit: 20
    t.string "meds_12_dose", limit: 20
    t.string "meds_13", limit: 20
    t.string "meds_13_dose", limit: 20
    t.string "meds_14", limit: 20
    t.string "meds_14_dose", limit: 20
    t.text "meds_cont"
    t.integer "meds_directed"
    t.text "meds_directed_comments"
    t.string "verified_by", limit: 20
  end

  create_table "medications_review_baseline", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.string "q2_med_01", limit: 30
    t.string "q2_med_01_dose", limit: 30
    t.date "q2_med_01_start"
    t.string "q2_med_02", limit: 30
    t.string "q2_med_02_dose", limit: 30
    t.date "q2_med_02_start"
    t.string "q2_med_03", limit: 30
    t.string "q2_med_03_dose", limit: 30
    t.date "q2_med_03_start"
    t.string "q2_med_04", limit: 30
    t.string "q2_med_04_dose", limit: 30
    t.date "q2_med_04_start"
    t.string "q2_med_05", limit: 30
    t.string "q2_med_05_dose", limit: 30
    t.date "q2_med_05_start"
    t.string "q2_med_06", limit: 30
    t.string "q2_med_06_dose", limit: 30
    t.date "q2_med_06_start"
    t.string "q2_med_07", limit: 30
    t.string "q2_med_07_dose", limit: 30
    t.date "q2_med_07_start"
    t.string "q2_med_08", limit: 30
    t.string "q2_med_08_dose", limit: 30
    t.date "q2_med_08_start"
    t.string "q2_med_09", limit: 30
    t.string "q2_med_09_dose", limit: 30
    t.date "q2_med_09_start"
    t.string "q2_med_10", limit: 30
    t.string "q2_med_10_dose", limit: 30
    t.date "q2_med_10_start"
    t.string "q2_med_11", limit: 30
    t.string "q2_med_11_dose", limit: 30
    t.date "q2_med_11_start"
    t.string "q2_med_12", limit: 30
    t.string "q2_med_12_dose", limit: 30
    t.date "q2_med_12_start"
    t.string "q2_med_13", limit: 30
    t.string "q2_med_13_dose", limit: 30
    t.date "q2_med_13_start"
    t.string "q2_med_14", limit: 30
    t.string "q2_med_14_dose", limit: 30
    t.date "q2_med_14_start"
    t.string "q2_med_15", limit: 30
    t.string "q2_med_15_dose", limit: 30
    t.date "q2_med_15_start"
    t.text "q2_med_other"
    t.integer "q3"
    t.text "q3_comments"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "medications_review_followup", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.string "q1_medchange_01", limit: 30
    t.string "q1_medchange_01_dose", limit: 30
    t.date "q1_medchange_01_date"
    t.string "q1_medchange_02", limit: 30
    t.string "q1_medchange_02_dose", limit: 30
    t.date "q1_medchange_02_date"
    t.string "q1_medchange_03", limit: 30
    t.string "q1_medchange_03_dose", limit: 30
    t.date "q1_medchange_03_date"
    t.string "q1_medchange_04", limit: 30
    t.string "q1_medchange_04_dose", limit: 30
    t.date "q1_medchange_04_date"
    t.string "q1_medchange_05", limit: 30
    t.string "q1_medchange_05_dose", limit: 30
    t.date "q1_medchange_05_date"
    t.text "q1_medchange_other"
    t.integer "q2"
    t.text "q2_comments"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "midas_raw_scored", force: :cascade do |t|
    t.integer "subject_id", null: false
    t.date "date", null: false
    t.integer "visit_num", null: false
    t.integer "study_id", null: false
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "total"
    t.integer "midas_score"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "mini_lifetime_substance_disorders", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "lifetime_alcohol_dependence"
    t.integer "lifetime_alcohol_abuse"
    t.integer "lifetime_substance_dependence"
    t.text "dependence_substances_used"
    t.integer "lifetime_substance_abuse"
    t.text "abuse_substances_used"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "mini_scored", force: :cascade do |t|
    t.bigint "subject_id", null: false
    t.date "date", null: false
    t.bigint "visit_num"
    t.integer "study_id"
    t.integer "mde_current"
    t.integer "mde_recurrent"
    t.integer "mde_melancholic"
    t.integer "dysthymia"
    t.integer "suicidality"
    t.integer "suicidality_risk"
    t.integer "manic_current"
    t.integer "manic_past"
    t.integer "hypomanic_current"
    t.integer "hypomanic_past"
    t.integer "panic_disorder_current"
    t.integer "panic_disorder_lifetime"
    t.integer "agoraphobia"
    t.integer "social_phobia"
    t.integer "ocd"
    t.integer "ptsd"
    t.integer "alcohol_dependence"
    t.integer "alcohol_abuse"
    t.bigint "substance_dependence"
    t.text "dependence_substances_used"
    t.integer "substance_abuse"
    t.text "abuse_substances_used"
    t.integer "psychotic_current"
    t.integer "psychotic_lifetime"
    t.integer "mood_current"
    t.integer "mood_lifetime"
    t.integer "anorexia"
    t.integer "bulimia"
    t.integer "anorexia_binge"
    t.integer "gad"
    t.integer "antisocial"
    t.string "verified_by", limit: 10
    t.string "administrator", limit: 20
  end

  create_table "mmpi_full", id: false, force: :cascade do |t|
    t.bigint "study_id", null: false
    t.integer "clientid"
    t.date "birthdate"
    t.date "admindate"
    t.integer "gender"
    t.string "yrsofeduc", limit: 2
    t.string "maritalstat", limit: 1
    t.integer "ethnicind"
    t.integer "ethnicasn"
    t.integer "ethnicblk"
    t.integer "ethnichis"
    t.integer "ethnichaw"
    t.integer "ethnicwht"
    t.integer "ethnicoth"
    t.string "lastname", limit: 1
    t.string "firstname", limit: 1
    t.string "mi", limit: 1
    t.string "lithocode", limit: 1
    t.string "custom1", limit: 1
    t.string "custom2", limit: 1
    t.string "custom3", limit: 1
    t.string "custom4", limit: 1
    t.integer "ngt_vrinr"
    t.integer "ngt_trinr"
    t.string "trinstr_rf", limit: 1
    t.integer "ngt_fr"
    t.integer "ngt_fpr"
    t.integer "ngt_fs"
    t.integer "ngt_fbsr"
    t.integer "ngt_rbs"
    t.integer "ngt_lr"
    t.integer "ngt_kr"
    t.integer "ngt_eid"
    t.integer "ngt_thd"
    t.integer "ngt_bxd"
    t.integer "ngt_rcd_rf"
    t.integer "ngt_rc1_rf"
    t.integer "ngt_rc2_rf"
    t.integer "ngt_rc3_rf"
    t.integer "ngt_rc4_rf"
    t.integer "ngt_rc6_rf"
    t.integer "ngt_rc7_rf"
    t.integer "ngt_rc8_rf"
    t.integer "ngt_rc9_rf"
    t.integer "ngt_mls"
    t.integer "ngt_hpc"
    t.integer "ngt_nuc"
    t.integer "ngt_gic"
    t.integer "ngt_sui"
    t.integer "ngt_hlp"
    t.integer "ngt_sfd"
    t.integer "ngt_nfc"
    t.integer "ngt_cog"
    t.integer "ngt_stw"
    t.integer "ngt_axy"
    t.integer "ngt_anp"
    t.integer "ngt_brf"
    t.integer "ngt_msf"
    t.integer "ngt_jcp"
    t.integer "ngt_sub"
    t.integer "ngt_agg"
    t.integer "ngt_act"
    t.integer "ngt_fml"
    t.integer "ngt_ipp"
    t.integer "ngt_sav"
    t.integer "ngt_shy"
    t.integer "ngt_dsf"
    t.integer "ngt_aes"
    t.integer "ngt_mec"
    t.integer "ngt_aggrr"
    t.integer "ngt_psycr"
    t.integer "ngt_discr"
    t.integer "ngt_neger"
    t.integer "ngt_intrr"
    t.integer "raw_vrinr"
    t.integer "raw_trinr"
    t.integer "raw_fr"
    t.integer "raw_fpr"
    t.integer "raw_fs"
    t.integer "raw_fbsr"
    t.integer "raw_rbs"
    t.integer "raw_lr"
    t.integer "raw_kr"
    t.integer "raw_eid"
    t.integer "raw_thd"
    t.integer "raw_bxd"
    t.integer "raw_rcd_rf"
    t.integer "raw_rc1_rf"
    t.integer "raw_rc2_rf"
    t.integer "raw_rc3_rf"
    t.integer "raw_rc4_rf"
    t.integer "raw_rc6_rf"
    t.integer "raw_rc7_rf"
    t.integer "raw_rc8_rf"
    t.integer "raw_rc9_rf"
    t.integer "raw_mls"
    t.integer "raw_hpc"
    t.integer "raw_nuc"
    t.integer "raw_gic"
    t.integer "raw_sui"
    t.integer "raw_hlp"
    t.integer "raw_sfd"
    t.integer "raw_nfc"
    t.integer "raw_cog"
    t.integer "raw_stw"
    t.integer "raw_axy"
    t.integer "raw_anp"
    t.integer "raw_brf"
    t.integer "raw_msf"
    t.integer "raw_jcp"
    t.integer "raw_sub"
    t.integer "raw_agg"
    t.integer "raw_act"
    t.integer "raw_fml"
    t.integer "raw_ipp"
    t.integer "raw_sav"
    t.integer "raw_shy"
    t.integer "raw_dsf"
    t.integer "raw_aes"
    t.integer "raw_mec"
    t.integer "raw_aggrr"
    t.integer "raw_psycr"
    t.integer "raw_discr"
    t.integer "raw_neger"
    t.integer "raw_intrr"
    t.integer "cannotsay_rf"
    t.integer "pcttrue_rf"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.string "q6", limit: 1
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.integer "q21"
    t.string "q22", limit: 1
    t.string "q23", limit: 1
    t.string "q24", limit: 1
    t.string "q25", limit: 1
    t.string "q26", limit: 1
    t.string "q27", limit: 1
    t.string "q28", limit: 1
    t.string "q29", limit: 1
    t.string "q30", limit: 1
    t.string "q31", limit: 1
    t.string "q32", limit: 1
    t.string "q33", limit: 1
    t.string "q34", limit: 1
    t.string "q35", limit: 1
    t.string "q36", limit: 1
    t.string "q37", limit: 1
    t.string "q38", limit: 1
    t.string "q39", limit: 1
    t.string "q40", limit: 1
    t.string "q41", limit: 1
    t.string "q42", limit: 1
    t.string "q43", limit: 1
    t.string "q44", limit: 1
    t.string "q45", limit: 1
    t.string "q46", limit: 1
    t.integer "q47"
    t.integer "q48"
    t.integer "q49"
    t.integer "q50"
    t.integer "q51"
    t.integer "q52"
    t.integer "q53"
    t.integer "q54"
    t.integer "q55"
    t.integer "q56"
    t.integer "q57"
    t.integer "q58"
    t.integer "q59"
    t.integer "q60"
    t.integer "q61"
    t.integer "q62"
    t.integer "q63"
    t.integer "q64"
    t.integer "q65"
    t.integer "q66"
    t.integer "q67"
    t.integer "q68"
    t.integer "q69"
    t.integer "q70"
    t.integer "q71"
    t.string "q72", limit: 1
    t.string "q73", limit: 1
    t.string "q74", limit: 1
    t.string "q75", limit: 1
    t.string "q76", limit: 1
    t.string "q77", limit: 1
    t.string "q78", limit: 1
    t.string "q79", limit: 1
    t.string "q80", limit: 1
    t.string "q81", limit: 1
    t.string "q82", limit: 1
    t.string "q83", limit: 1
    t.string "q84", limit: 1
    t.string "q85", limit: 1
    t.string "q86", limit: 1
    t.string "q87", limit: 1
    t.string "q88", limit: 1
    t.string "q89", limit: 1
    t.string "q90", limit: 1
    t.string "q91", limit: 1
    t.string "q92", limit: 1
    t.string "q93", limit: 1
    t.string "q94", limit: 1
    t.string "q95", limit: 1
    t.string "q96", limit: 1
    t.integer "q97"
    t.string "q98", limit: 1
    t.integer "q99"
    t.integer "q100"
    t.integer "q101"
    t.integer "q102"
    t.integer "q103"
    t.integer "q104"
    t.integer "q105"
    t.integer "q106"
    t.integer "q107"
    t.integer "q108"
    t.integer "q109"
    t.integer "q110"
    t.integer "q111"
    t.integer "q112"
    t.integer "q113"
    t.string "q114", limit: 1
    t.integer "q115"
    t.integer "q116"
    t.integer "q117"
    t.integer "q118"
    t.integer "q119"
    t.integer "q120"
    t.integer "q121"
    t.integer "q122"
    t.integer "q123"
    t.integer "q124"
    t.integer "q125"
    t.integer "q126"
    t.integer "q127"
    t.integer "q128"
    t.integer "q129"
    t.integer "q130"
    t.integer "q131"
    t.integer "q132"
    t.integer "q133"
    t.integer "q134"
    t.integer "q135"
    t.integer "q136"
    t.integer "q137"
    t.integer "q138"
    t.integer "q139"
    t.integer "q140"
    t.integer "q141"
    t.integer "q142"
    t.integer "q143"
    t.integer "q144"
    t.string "q145", limit: 1
    t.integer "q146"
    t.integer "q147"
    t.integer "q148"
    t.integer "q149"
    t.integer "q150"
    t.integer "q151"
    t.integer "q152"
    t.integer "q153"
    t.integer "q154"
    t.integer "q155"
    t.integer "q156"
    t.integer "q157"
    t.integer "q158"
    t.integer "q159"
    t.integer "q160"
    t.integer "q161"
    t.integer "q162"
    t.integer "q163"
    t.integer "q164"
    t.integer "q165"
    t.integer "q166"
    t.integer "q167"
    t.string "q168", limit: 1
    t.integer "q169"
    t.integer "q170"
    t.integer "q171"
    t.integer "q172"
    t.string "q173", limit: 1
    t.string "q174", limit: 1
    t.string "q175", limit: 1
    t.integer "q176"
    t.integer "q177"
    t.integer "q178"
    t.integer "q179"
    t.integer "q180"
    t.integer "q181"
    t.integer "q182"
    t.integer "q183"
    t.integer "q184"
    t.integer "q185"
    t.integer "q186"
    t.integer "q187"
    t.integer "q188"
    t.integer "q189"
    t.integer "q190"
    t.integer "q191"
    t.integer "q192"
    t.integer "q193"
    t.integer "q194"
    t.integer "q195"
    t.integer "q196"
    t.integer "q197"
    t.integer "q198"
    t.integer "q199"
    t.integer "q200"
    t.integer "q201"
    t.integer "q202"
    t.integer "q203"
    t.integer "q204"
    t.integer "q205"
    t.integer "q206"
    t.integer "q207"
    t.integer "q208"
    t.integer "q209"
    t.integer "q210"
    t.integer "q211"
    t.integer "q212"
    t.integer "q213"
    t.integer "q214"
    t.integer "q215"
    t.integer "q216"
    t.integer "q217"
    t.integer "q218"
    t.integer "q219"
    t.integer "q220"
    t.integer "q221"
    t.integer "q222"
    t.integer "q223"
    t.integer "q224"
    t.integer "q225"
    t.integer "q226"
    t.integer "q227"
    t.integer "q228"
    t.integer "q229"
    t.integer "q230"
    t.integer "q231"
    t.integer "q232"
    t.integer "q233"
    t.integer "q234"
    t.integer "q235"
    t.integer "q236"
    t.integer "q237"
    t.integer "q238"
    t.integer "q239"
    t.integer "q240"
    t.integer "q241"
    t.integer "q242"
    t.integer "q243"
    t.string "q244", limit: 1
    t.integer "q245"
    t.integer "q246"
    t.integer "q247"
    t.integer "q248"
    t.integer "q249"
    t.integer "q250"
    t.integer "q251"
    t.integer "q252"
    t.integer "q253"
    t.integer "q254"
    t.integer "q255"
    t.integer "q256"
    t.integer "q257"
    t.integer "q258"
    t.integer "q259"
    t.integer "q260"
    t.integer "q261"
    t.integer "q262"
    t.integer "q263"
    t.integer "q264"
    t.integer "q265"
    t.integer "q266"
    t.integer "q267"
    t.integer "q268"
    t.integer "q269"
    t.integer "q270"
    t.integer "q271"
    t.integer "q272"
    t.integer "q273"
    t.integer "q274"
    t.integer "q275"
    t.integer "q276"
    t.integer "q277"
    t.integer "q278"
    t.integer "q279"
    t.integer "q280"
    t.integer "q281"
    t.integer "q282"
    t.integer "q283"
    t.integer "q284"
    t.integer "q285"
    t.integer "q286"
    t.integer "q287"
    t.integer "q288"
    t.integer "q289"
    t.integer "q290"
    t.integer "q291"
    t.integer "q292"
    t.integer "q293"
    t.integer "q294"
    t.integer "q295"
    t.integer "q296"
    t.integer "q297"
    t.integer "q298"
    t.integer "q299"
    t.integer "q300"
    t.integer "q301"
    t.string "q302", limit: 1
    t.integer "q303"
    t.integer "q304"
    t.integer "q305"
    t.integer "q306"
    t.integer "q307"
    t.integer "q308"
    t.string "q309", limit: 1
    t.integer "q310"
    t.integer "q311"
    t.integer "q312"
    t.integer "q313"
    t.integer "q314"
    t.integer "q315"
    t.integer "q316"
    t.integer "q317"
    t.integer "q318"
    t.integer "q319"
    t.integer "q320"
    t.integer "q321"
    t.integer "q322"
    t.integer "q323"
    t.integer "q324"
    t.integer "q325"
    t.integer "q326"
    t.integer "q327"
    t.integer "q328"
    t.integer "q329"
    t.integer "q330"
    t.integer "q331"
    t.integer "q332"
    t.integer "q333"
    t.integer "q334"
    t.integer "q335"
    t.integer "q336"
    t.integer "q337"
    t.integer "q338"
  end

  create_table "mmpi_rf_combined_scores", id: :serial, force: :cascade do |t|
    t.integer "subjectid"
    t.date "birthdate"
    t.date "admindate"
    t.integer "study_id"
    t.integer "ngt_vrinr"
    t.integer "ngt_trinr"
    t.string "trinstr_rf", limit: 1
    t.integer "ngt_fr"
    t.integer "ngt_fpr"
    t.integer "ngt_fs"
    t.integer "ngt_fbsr"
    t.integer "ngt_rbs"
    t.integer "ngt_lr"
    t.integer "ngt_kr"
    t.integer "ngt_eid"
    t.integer "ngt_thd"
    t.integer "ngt_bxd"
    t.integer "ngt_rcd_rf"
    t.integer "ngt_rc1_rf"
    t.integer "ngt_rc2_rf"
    t.integer "ngt_rc3_rf"
    t.integer "ngt_rc4_rf"
    t.integer "ngt_rc6_rf"
    t.integer "ngt_rc7_rf"
    t.integer "ngt_rc8_rf"
    t.integer "ngt_rc9_rf"
    t.integer "ngt_mls"
    t.integer "ngt_hpc"
    t.integer "ngt_nuc"
    t.integer "ngt_gic"
    t.integer "ngt_sui"
    t.integer "ngt_hlp"
    t.integer "ngt_sfd"
    t.integer "ngt_nfc"
    t.integer "ngt_cog"
    t.integer "ngt_stw"
    t.integer "ngt_axy"
    t.integer "ngt_anp"
    t.integer "ngt_brf"
    t.integer "ngt_msf"
    t.integer "ngt_jcp"
    t.integer "ngt_sub"
    t.integer "ngt_agg"
    t.integer "ngt_act"
    t.integer "ngt_fml"
    t.integer "ngt_ipp"
    t.integer "ngt_sav"
    t.integer "ngt_shy"
    t.integer "ngt_dsf"
    t.integer "ngt_aes"
    t.integer "ngt_mec"
    t.integer "ngt_aggrr"
    t.integer "ngt_psycr"
    t.integer "ngt_discr"
    t.integer "ngt_neger"
    t.integer "ngt_intrr"
    t.integer "raw_vrinr"
    t.integer "raw_trinr"
    t.integer "raw_fr"
    t.integer "raw_fpr"
    t.integer "raw_fs"
    t.integer "raw_fbsr"
    t.integer "raw_rbs"
    t.integer "raw_lr"
    t.integer "raw_kr"
    t.integer "raw_eid"
    t.integer "raw_thd"
    t.integer "raw_bxd"
    t.integer "raw_rcd_rf"
    t.integer "raw_rc1_rf"
    t.integer "raw_rc2_rf"
    t.integer "raw_rc3_rf"
    t.integer "raw_rc4_rf"
    t.integer "raw_rc6_rf"
    t.integer "raw_rc7_rf"
    t.integer "raw_rc8_rf"
    t.integer "raw_rc9_rf"
    t.integer "raw_mls"
    t.integer "raw_hpc"
    t.integer "raw_nuc"
    t.integer "raw_gic"
    t.integer "raw_sui"
    t.integer "raw_hlp"
    t.integer "raw_sfd"
    t.integer "raw_nfc"
    t.integer "raw_cog"
    t.integer "raw_stw"
    t.integer "raw_axy"
    t.integer "raw_anp"
    t.integer "raw_brf"
    t.integer "raw_msf"
    t.integer "raw_jcp"
    t.integer "raw_sub"
    t.integer "raw_agg"
    t.integer "raw_act"
    t.integer "raw_fml"
    t.integer "raw_ipp"
    t.integer "raw_sav"
    t.integer "raw_shy"
    t.integer "raw_dsf"
    t.integer "raw_aes"
    t.integer "raw_mec"
    t.integer "raw_aggrr"
    t.integer "raw_psycr"
    t.integer "raw_discr"
    t.integer "raw_neger"
    t.integer "raw_intrr"
    t.integer "cannotsay_rf"
    t.integer "pcttrue_rf"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.integer "q21"
    t.integer "q22"
    t.integer "q23"
    t.integer "q24"
    t.integer "q25"
    t.integer "q26"
    t.integer "q27"
    t.integer "q28"
    t.integer "q29"
    t.integer "q30"
    t.integer "q31"
    t.integer "q32"
    t.integer "q33"
    t.integer "q34"
    t.integer "q35"
    t.integer "q36"
    t.integer "q37"
    t.integer "q38"
    t.integer "q39"
    t.integer "q40"
    t.integer "q41"
    t.integer "q42"
    t.integer "q43"
    t.integer "q44"
    t.integer "q45"
    t.integer "q46"
    t.integer "q47"
    t.integer "q48"
    t.integer "q49"
    t.integer "q50"
    t.integer "q51"
    t.integer "q52"
    t.integer "q53"
    t.integer "q54"
    t.integer "q55"
    t.integer "q56"
    t.integer "q57"
    t.integer "q58"
    t.integer "q59"
    t.integer "q60"
    t.integer "q61"
    t.integer "q62"
    t.integer "q63"
    t.integer "q64"
    t.integer "q65"
    t.integer "q66"
    t.integer "q67"
    t.integer "q68"
    t.integer "q69"
    t.integer "q70"
    t.integer "q71"
    t.integer "q72"
    t.integer "q73"
    t.integer "q74"
    t.integer "q75"
    t.integer "q76"
    t.integer "q77"
    t.integer "q78"
    t.integer "q79"
    t.integer "q80"
    t.integer "q81"
    t.integer "q82"
    t.integer "q83"
    t.string "q84", limit: 1
    t.integer "q85"
    t.integer "q86"
    t.integer "q87"
    t.integer "q88"
    t.integer "q89"
    t.integer "q90"
    t.integer "q91"
    t.integer "q92"
    t.integer "q93"
    t.integer "q94"
    t.integer "q95"
    t.integer "q96"
    t.integer "q97"
    t.integer "q98"
    t.integer "q99"
    t.integer "q100"
    t.integer "q101"
    t.integer "q102"
    t.integer "q103"
    t.integer "q104"
    t.integer "q105"
    t.integer "q106"
    t.integer "q107"
    t.integer "q108"
    t.integer "q109"
    t.integer "q110"
    t.integer "q111"
    t.integer "q112"
    t.integer "q113"
    t.integer "q114"
    t.integer "q115"
    t.integer "q116"
    t.integer "q117"
    t.integer "q118"
    t.integer "q119"
    t.integer "q120"
    t.integer "q121"
    t.integer "q122"
    t.integer "q123"
    t.integer "q124"
    t.integer "q125"
    t.integer "q126"
    t.integer "q127"
    t.integer "q128"
    t.integer "q129"
    t.integer "q130"
    t.integer "q131"
    t.integer "q132"
    t.integer "q133"
    t.integer "q134"
    t.integer "q135"
    t.integer "q136"
    t.integer "q137"
    t.integer "q138"
    t.integer "q139"
    t.integer "q140"
    t.integer "q141"
    t.integer "q142"
    t.integer "q143"
    t.integer "q144"
    t.integer "q145"
    t.integer "q146"
    t.integer "q147"
    t.integer "q148"
    t.integer "q149"
    t.integer "q150"
    t.integer "q151"
    t.integer "q152"
    t.integer "q153"
    t.integer "q154"
    t.integer "q155"
    t.integer "q156"
    t.integer "q157"
    t.integer "q158"
    t.integer "q159"
    t.integer "q160"
    t.integer "q161"
    t.integer "q162"
    t.integer "q163"
    t.integer "q164"
    t.integer "q165"
    t.integer "q166"
    t.integer "q167"
    t.integer "q168"
    t.integer "q169"
    t.integer "q170"
    t.integer "q171"
    t.integer "q172"
    t.integer "q173"
    t.integer "q174"
    t.integer "q175"
    t.integer "q176"
    t.integer "q177"
    t.integer "q178"
    t.integer "q179"
    t.integer "q180"
    t.integer "q181"
    t.integer "q182"
    t.integer "q183"
    t.integer "q184"
    t.integer "q185"
    t.integer "q186"
    t.integer "q187"
    t.integer "q188"
    t.integer "q189"
    t.integer "q190"
    t.integer "q191"
    t.integer "q192"
    t.integer "q193"
    t.integer "q194"
    t.integer "q195"
    t.integer "q196"
    t.integer "q197"
    t.integer "q198"
    t.integer "q199"
    t.integer "q200"
    t.integer "q201"
    t.integer "q202"
    t.integer "q203"
    t.integer "q204"
    t.integer "q205"
    t.integer "q206"
    t.integer "q207"
    t.integer "q208"
    t.integer "q209"
    t.integer "q210"
    t.integer "q211"
    t.integer "q212"
    t.integer "q213"
    t.integer "q214"
    t.integer "q215"
    t.integer "q216"
    t.integer "q217"
    t.integer "q218"
    t.integer "q219"
    t.integer "q220"
    t.integer "q221"
    t.integer "q222"
    t.integer "q223"
    t.integer "q224"
    t.integer "q225"
    t.integer "q226"
    t.integer "q227"
    t.integer "q228"
    t.integer "q229"
    t.integer "q230"
    t.integer "q231"
    t.integer "q232"
    t.integer "q233"
    t.integer "q234"
    t.integer "q235"
    t.integer "q236"
    t.integer "q237"
    t.integer "q238"
    t.integer "q239"
    t.integer "q240"
    t.integer "q241"
    t.integer "q242"
    t.integer "q243"
    t.integer "q244"
    t.integer "q245"
    t.integer "q246"
    t.integer "q247"
    t.integer "q248"
    t.integer "q249"
    t.integer "q250"
    t.integer "q251"
    t.integer "q252"
    t.integer "q253"
    t.integer "q254"
    t.integer "q255"
    t.integer "q256"
    t.integer "q257"
    t.integer "q258"
    t.integer "q259"
    t.integer "q260"
    t.integer "q261"
    t.integer "q262"
    t.integer "q263"
    t.integer "q264"
    t.integer "q265"
    t.integer "q266"
    t.integer "q267"
    t.integer "q268"
    t.integer "q269"
    t.integer "q270"
    t.integer "q271"
    t.integer "q272"
    t.integer "q273"
    t.integer "q274"
    t.integer "q275"
    t.integer "q276"
    t.integer "q277"
    t.integer "q278"
    t.integer "q279"
    t.integer "q280"
    t.integer "q281"
    t.integer "q282"
    t.integer "q283"
    t.integer "q284"
    t.integer "q285"
    t.integer "q286"
    t.integer "q287"
    t.integer "q288"
    t.integer "q289"
    t.integer "q290"
    t.integer "q291"
    t.integer "q292"
    t.integer "q293"
    t.integer "q294"
    t.integer "q295"
    t.integer "q296"
    t.integer "q297"
    t.integer "q298"
    t.integer "q299"
    t.integer "q300"
    t.integer "q301"
    t.integer "q302"
    t.integer "q303"
    t.integer "q304"
    t.integer "q305"
    t.integer "q306"
    t.integer "q307"
    t.integer "q308"
    t.integer "q309"
    t.integer "q310"
    t.integer "q311"
    t.integer "q312"
    t.integer "q313"
    t.integer "q314"
    t.integer "q315"
    t.integer "q316"
    t.integer "q317"
    t.integer "q318"
    t.integer "q319"
    t.integer "q320"
    t.integer "q321"
    t.integer "q322"
    t.integer "q323"
    t.integer "q324"
    t.integer "q325"
    t.integer "q326"
    t.integer "q327"
    t.integer "q328"
    t.integer "q329"
    t.integer "q330"
    t.integer "q331"
    t.integer "q332"
    t.integer "q333"
    t.integer "q334"
    t.integer "q335"
    t.integer "q336"
    t.integer "q337"
    t.integer "q338"
    t.date "time_stamp"
    t.string "uploaded_by", limit: 10
  end

  create_table "mmpi_rf_raw", id: false, force: :cascade do |t|
    t.integer "id", default: 0, null: false
    t.integer "subjectid"
    t.date "birthdate"
    t.date "admindate"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.integer "q21"
    t.integer "q22"
    t.integer "q23"
    t.integer "q24"
    t.integer "q25"
    t.integer "q26"
    t.integer "q27"
    t.integer "q28"
    t.integer "q29"
    t.integer "q30"
    t.integer "q31"
    t.integer "q32"
    t.integer "q33"
    t.integer "q34"
    t.integer "q35"
    t.integer "q36"
    t.integer "q37"
    t.integer "q38"
    t.integer "q39"
    t.integer "q40"
    t.integer "q41"
    t.integer "q42"
    t.integer "q43"
    t.integer "q44"
    t.integer "q45"
    t.integer "q46"
    t.integer "q47"
    t.integer "q48"
    t.integer "q49"
    t.integer "q50"
    t.integer "q51"
    t.integer "q52"
    t.integer "q53"
    t.integer "q54"
    t.integer "q55"
    t.integer "q56"
    t.integer "q57"
    t.integer "q58"
    t.integer "q59"
    t.integer "q60"
    t.integer "q61"
    t.integer "q62"
    t.integer "q63"
    t.integer "q64"
    t.integer "q65"
    t.integer "q66"
    t.integer "q67"
    t.integer "q68"
    t.integer "q69"
    t.integer "q70"
    t.integer "q71"
    t.integer "q72"
    t.integer "q73"
    t.integer "q74"
    t.integer "q75"
    t.integer "q76"
    t.integer "q77"
    t.integer "q78"
    t.integer "q79"
    t.integer "q80"
    t.integer "q81"
    t.integer "q82"
    t.integer "q83"
    t.string "q84", limit: 1
    t.integer "q85"
    t.integer "q86"
    t.integer "q87"
    t.integer "q88"
    t.integer "q89"
    t.integer "q90"
    t.integer "q91"
    t.integer "q92"
    t.integer "q93"
    t.integer "q94"
    t.integer "q95"
    t.integer "q96"
    t.integer "q97"
    t.integer "q98"
    t.integer "q99"
    t.integer "q100"
    t.integer "q101"
    t.integer "q102"
    t.integer "q103"
    t.integer "q104"
    t.integer "q105"
    t.integer "q106"
    t.integer "q107"
    t.integer "q108"
    t.integer "q109"
    t.integer "q110"
    t.integer "q111"
    t.integer "q112"
    t.integer "q113"
    t.integer "q114"
    t.integer "q115"
    t.integer "q116"
    t.integer "q117"
    t.integer "q118"
    t.integer "q119"
    t.integer "q120"
    t.integer "q121"
    t.integer "q122"
    t.integer "q123"
    t.integer "q124"
    t.integer "q125"
    t.integer "q126"
    t.integer "q127"
    t.integer "q128"
    t.integer "q129"
    t.integer "q130"
    t.integer "q131"
    t.integer "q132"
    t.integer "q133"
    t.integer "q134"
    t.integer "q135"
    t.integer "q136"
    t.integer "q137"
    t.integer "q138"
    t.integer "q139"
    t.integer "q140"
    t.integer "q141"
    t.integer "q142"
    t.integer "q143"
    t.integer "q144"
    t.integer "q145"
    t.integer "q146"
    t.integer "q147"
    t.integer "q148"
    t.integer "q149"
    t.integer "q150"
    t.integer "q151"
    t.integer "q152"
    t.integer "q153"
    t.integer "q154"
    t.integer "q155"
    t.integer "q156"
    t.integer "q157"
    t.integer "q158"
    t.integer "q159"
    t.integer "q160"
    t.integer "q161"
    t.integer "q162"
    t.integer "q163"
    t.integer "q164"
    t.integer "q165"
    t.integer "q166"
    t.integer "q167"
    t.integer "q168"
    t.integer "q169"
    t.integer "q170"
    t.integer "q171"
    t.integer "q172"
    t.integer "q173"
    t.integer "q174"
    t.integer "q175"
    t.integer "q176"
    t.integer "q177"
    t.integer "q178"
    t.integer "q179"
    t.integer "q180"
    t.integer "q181"
    t.integer "q182"
    t.integer "q183"
    t.integer "q184"
    t.integer "q185"
    t.integer "q186"
    t.integer "q187"
    t.integer "q188"
    t.integer "q189"
    t.integer "q190"
    t.integer "q191"
    t.integer "q192"
    t.integer "q193"
    t.integer "q194"
    t.integer "q195"
    t.integer "q196"
    t.integer "q197"
    t.integer "q198"
    t.integer "q199"
    t.integer "q200"
    t.integer "q201"
    t.integer "q202"
    t.integer "q203"
    t.integer "q204"
    t.integer "q205"
    t.integer "q206"
    t.integer "q207"
    t.integer "q208"
    t.integer "q209"
    t.integer "q210"
    t.integer "q211"
    t.integer "q212"
    t.integer "q213"
    t.integer "q214"
    t.integer "q215"
    t.integer "q216"
    t.integer "q217"
    t.integer "q218"
    t.integer "q219"
    t.integer "q220"
    t.integer "q221"
    t.integer "q222"
    t.integer "q223"
    t.integer "q224"
    t.integer "q225"
    t.integer "q226"
    t.integer "q227"
    t.integer "q228"
    t.integer "q229"
    t.integer "q230"
    t.integer "q231"
    t.integer "q232"
    t.integer "q233"
    t.integer "q234"
    t.integer "q235"
    t.integer "q236"
    t.integer "q237"
    t.integer "q238"
    t.integer "q239"
    t.integer "q240"
    t.integer "q241"
    t.integer "q242"
    t.integer "q243"
    t.integer "q244"
    t.integer "q245"
    t.integer "q246"
    t.integer "q247"
    t.integer "q248"
    t.integer "q249"
    t.integer "q250"
    t.integer "q251"
    t.integer "q252"
    t.integer "q253"
    t.integer "q254"
    t.integer "q255"
    t.integer "q256"
    t.integer "q257"
    t.integer "q258"
    t.integer "q259"
    t.integer "q260"
    t.integer "q261"
    t.integer "q262"
    t.integer "q263"
    t.integer "q264"
    t.integer "q265"
    t.integer "q266"
    t.integer "q267"
    t.integer "q268"
    t.integer "q269"
    t.integer "q270"
    t.integer "q271"
    t.integer "q272"
    t.integer "q273"
    t.integer "q274"
    t.integer "q275"
    t.integer "q276"
    t.integer "q277"
    t.integer "q278"
    t.integer "q279"
    t.integer "q280"
    t.integer "q281"
    t.integer "q282"
    t.integer "q283"
    t.integer "q284"
    t.integer "q285"
    t.integer "q286"
    t.integer "q287"
    t.integer "q288"
    t.integer "q289"
    t.integer "q290"
    t.integer "q291"
    t.integer "q292"
    t.integer "q293"
    t.integer "q294"
    t.integer "q295"
    t.integer "q296"
    t.integer "q297"
    t.integer "q298"
    t.integer "q299"
    t.integer "q300"
    t.integer "q301"
    t.integer "q302"
    t.integer "q303"
    t.integer "q304"
    t.integer "q305"
    t.integer "q306"
    t.integer "q307"
    t.integer "q308"
    t.integer "q309"
    t.integer "q310"
    t.integer "q311"
    t.integer "q312"
    t.integer "q313"
    t.integer "q314"
    t.integer "q315"
    t.integer "q316"
    t.integer "q317"
    t.integer "q318"
    t.integer "q319"
    t.integer "q320"
    t.integer "q321"
    t.integer "q322"
    t.integer "q323"
    t.integer "q324"
    t.integer "q325"
    t.integer "q326"
    t.integer "q327"
    t.integer "q328"
    t.integer "q329"
    t.integer "q330"
    t.integer "q331"
    t.integer "q332"
    t.integer "q333"
    t.integer "q334"
    t.integer "q335"
    t.integer "q336"
    t.integer "q337"
    t.integer "q338"
    t.date "time_stamp"
    t.string "uploaded_by", limit: 10
  end

  create_table "mmpi_rf_scored", id: false, force: :cascade do |t|
    t.integer "id", default: 0, null: false
    t.integer "subjectid"
    t.date "birthdate"
    t.date "admindate"
    t.integer "study_id"
    t.integer "ngt_vrinr"
    t.integer "ngt_trinr"
    t.string "trinstr_rf", limit: 1
    t.integer "ngt_fr"
    t.integer "ngt_fpr"
    t.integer "ngt_fs"
    t.integer "ngt_fbsr"
    t.integer "ngt_rbs"
    t.integer "ngt_lr"
    t.integer "ngt_kr"
    t.integer "ngt_eid"
    t.integer "ngt_thd"
    t.integer "ngt_bxd"
    t.integer "ngt_rcd_rf"
    t.integer "ngt_rc1_rf"
    t.integer "ngt_rc2_rf"
    t.integer "ngt_rc3_rf"
    t.integer "ngt_rc4_rf"
    t.integer "ngt_rc6_rf"
    t.integer "ngt_rc7_rf"
    t.integer "ngt_rc8_rf"
    t.integer "ngt_rc9_rf"
    t.integer "ngt_mls"
    t.integer "ngt_hpc"
    t.integer "ngt_nuc"
    t.integer "ngt_gic"
    t.integer "ngt_sui"
    t.integer "ngt_hlp"
    t.integer "ngt_sfd"
    t.integer "ngt_nfc"
    t.integer "ngt_cog"
    t.integer "ngt_stw"
    t.integer "ngt_axy"
    t.integer "ngt_anp"
    t.integer "ngt_brf"
    t.integer "ngt_msf"
    t.integer "ngt_jcp"
    t.integer "ngt_sub"
    t.integer "ngt_agg"
    t.integer "ngt_act"
    t.integer "ngt_fml"
    t.integer "ngt_ipp"
    t.integer "ngt_sav"
    t.integer "ngt_shy"
    t.integer "ngt_dsf"
    t.integer "ngt_aes"
    t.integer "ngt_mec"
    t.integer "ngt_aggrr"
    t.integer "ngt_psycr"
    t.integer "ngt_discr"
    t.integer "ngt_neger"
    t.integer "ngt_intrr"
    t.integer "raw_vrinr"
    t.integer "raw_trinr"
    t.integer "raw_fr"
    t.integer "raw_fpr"
    t.integer "raw_fs"
    t.integer "raw_fbsr"
    t.integer "raw_rbs"
    t.integer "raw_lr"
    t.integer "raw_kr"
    t.integer "raw_eid"
    t.integer "raw_thd"
    t.integer "raw_bxd"
    t.integer "raw_rcd_rf"
    t.integer "raw_rc1_rf"
    t.integer "raw_rc2_rf"
    t.integer "raw_rc3_rf"
    t.integer "raw_rc4_rf"
    t.integer "raw_rc6_rf"
    t.integer "raw_rc7_rf"
    t.integer "raw_rc8_rf"
    t.integer "raw_rc9_rf"
    t.integer "raw_mls"
    t.integer "raw_hpc"
    t.integer "raw_nuc"
    t.integer "raw_gic"
    t.integer "raw_sui"
    t.integer "raw_hlp"
    t.integer "raw_sfd"
    t.integer "raw_nfc"
    t.integer "raw_cog"
    t.integer "raw_stw"
    t.integer "raw_axy"
    t.integer "raw_anp"
    t.integer "raw_brf"
    t.integer "raw_msf"
    t.integer "raw_jcp"
    t.integer "raw_sub"
    t.integer "raw_agg"
    t.integer "raw_act"
    t.integer "raw_fml"
    t.integer "raw_ipp"
    t.integer "raw_sav"
    t.integer "raw_shy"
    t.integer "raw_dsf"
    t.integer "raw_aes"
    t.integer "raw_mec"
    t.integer "raw_aggrr"
    t.integer "raw_psycr"
    t.integer "raw_discr"
    t.integer "raw_neger"
    t.integer "raw_intrr"
    t.integer "cannotsay_rf"
    t.integer "pcttrue_rf"
    t.date "time_stamp"
    t.string "uploaded_by", limit: 10
  end

  create_table "mmse_raw_scored", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "q1"
    t.integer "q2"
    t.bigint "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "total"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "mnbest_consensus_summary", id: false, force: :cascade do |t|
    t.integer "id"
    t.integer "subject_id"
    t.string "date", limit: 10
    t.integer "visit_num"
    t.integer "study_id"
    t.string "blast_exposures", limit: 5
    t.string "blast_severity_1", limit: 1
    t.string "blast_severity_1_date", limit: 10
    t.string "blast_severity_2", limit: 1
    t.string "blast_severity_2_date", limit: 10
    t.string "blast_severity_3", limit: 1
    t.string "blast_severity_3_date", limit: 10
    t.integer "blast_severity_total"
    t.integer "blast_prob_def"
    t.integer "blast_poss_prob_def"
    t.integer "blast_unlikely_poss_prob_def"
    t.integer "blast_moderate_severe"
    t.integer "nonblast_exposures"
    t.string "nonblast_severity_1", limit: 2
    t.string "nonblast_severity_1_date", limit: 10
    t.string "nonblast_severity_2", limit: 1
    t.string "nonblast_severity_2_date", limit: 10
    t.string "nonblast_severity_3", limit: 1
    t.string "nonblast_severity_3_date", limit: 10
    t.integer "nonblast_severity_total"
    t.integer "nonblast_prob_def"
    t.integer "nonblast_poss_prob_def"
    t.integer "nonblast_unlikely_poss_prob_def"
    t.integer "nonblast_moderate_severe"
    t.string "administrator", limit: 21
    t.string "initial_tbi_classification", limit: 12
    t.string "consensus_tbi_classification", limit: 11
    t.string "consensus_date", limit: 10
    t.string "consensus_group", limit: 11
    t.string "verified_by", limit: 6
  end

  create_table "moca", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "visuospatial/executive"
    t.bigint "naming"
    t.bigint "attention_1"
    t.bigint "attention_2"
    t.bigint "attention_3"
    t.bigint "language_1"
    t.bigint "language_2"
    t.bigint "abstraction"
    t.bigint "delayed_recall"
    t.bigint "orientaion"
    t.bigint "education"
    t.bigint "total"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "mpai_raw", id: :serial, force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "mpai4c_1"
    t.bigint "mpai4c_2"
    t.bigint "mpai4c_3"
    t.bigint "mpai4c_4"
    t.bigint "mpai4c_5"
    t.bigint "mpai4c_6"
    t.bigint "mpai4c_7a"
    t.bigint "mpai4c_7b"
    t.bigint "mpai4c_7b_2"
    t.integer "mpai4c_8"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "mpai_scored", id: false, force: :cascade do |t|
    t.bigint "id"
    t.bigint "subject_id"
    t.string "date", limit: 255
    t.bigint "visit_num"
    t.bigint "study_id"
    t.string "administrator", limit: 255
    t.string "verified_by", limit: 255
    t.float "participation_total"
    t.bigint "participation_total_tscore"
  end

  create_table "n_back", id: false, force: :cascade do |t|
    t.string "subject_id", limit: 10
    t.string "date", limit: 10
    t.string "visit_num", limit: 10
    t.string "study_id", limit: 10
    t.string "success", limit: 100
    t.string "trial_type", limit: 100
    t.string "trial_index", limit: 100
    t.string "time_elapsed", limit: 100
    t.string "internal_node_id", limit: 100
    t.string "datetime_timestamp", limit: 100
    t.string "event_timestamp", limit: 100
    t.string "performance_stamp", limit: 100
    t.string "trigger", limit: 100
    t.string "rt", limit: 100
    t.string "responses", limit: 100
    t.string "view_history", limit: 100
    t.string "trial_id", limit: 100
    t.string "stimulus", limit: 100
    t.string "timestamp", limit: 100
    t.string "key_press", limit: 100
    t.string "trial_onset", limit: 100
    t.string "trial_loaded", limit: 100
    t.string "trial_finished", limit: 100
    t.string "correct_response", limit: 100
    t.string "mri", limit: 100
    t.string "duration", limit: 100
    t.string "n", limit: 100
    t.string "run_number", limit: 100
    t.string "performance", limit: 100
  end

  create_table "neuro_bart_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 20
    t.integer "subject_id"
    t.integer "visit_num"
    t.string "DataFile.Basename", limit: 25
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 7
    t.integer "group"
    t.integer "ntrials"
    t.integer "PayTotal(Session)"
    t.bigint "randomseed"
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "date", limit: 20
    t.string "sessionstartdatetimeutc", limit: 16
    t.string "sessiontime", limit: 8
    t.string "studioversion", limit: 10
    t.string "trialtitle", limit: 10
    t.integer "trial"
    t.integer "payperpump"
    t.integer "paypop"
    t.integer "PayTotal[Trial]"
    t.integer "PayTrial(Trial)"
    t.string "practicelist", limit: 1
    t.string "practicelist_cycle", limit: 1
    t.string "practicelist_sample", limit: 1
    t.string "Procedure(Trial)", limit: 9
    t.integer "PumpN(Trial)"
    t.integer "pumpnpop"
    t.string "pumpnpoplist", limit: 2
    t.string "Running(Trial)", limit: 12
    t.string "triallist", limit: 1
    t.string "triallist_cycle", limit: 1
    t.string "triallist_sample", limit: 2
    t.integer "sample"
    t.integer "bartslide_acc"
    t.string "bartslide_cresp", limit: 1
    t.string "bartslide_resp", limit: 1
    t.integer "bartslide_rt"
    t.integer "bartslide_rttime"
    t.integer "PayTrial(Sample)"
    t.string "Procedure(Sample)", limit: 8
    t.integer "PumpN(Sample)"
    t.string "Running(Sample)", limit: 8
    t.integer "size"
    t.integer "steplist"
    t.integer "steplist_cycle"
    t.integer "steplist_sample"
  end

  create_table "neuro_bart_scored", id: false, force: :cascade do |t|
    t.string "id", limit: 10
    t.integer "eprime_id"
    t.integer "subject_id"
    t.integer "visit_num"
    t.string "date", limit: 10
    t.integer "study_id"
    t.integer "trials"
    t.integer "adjusted_pumps"
  end

  create_table "neuro_final_screening_questionnaire", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.integer "study_id"
    t.string "living_independently", limit: 1
    t.string "give_consent", limit: 1
    t.string "comprehend_english", limit: 1
    t.string "ambulatory", limit: 1
    t.string "suicidal", limit: 1
    t.string "tbi", limit: 10
    t.string "injury", limit: 5
    t.string "injury_agent", limit: 3
    t.string "cause_of_injury", limit: 3
    t.string "type_of_injury", limit: 3
    t.string "alcohol_or_drug_related", limit: 3
    t.string "classification", limit: 10
    t.date "date_of_injury"
    t.string "blurred_vision", limit: 1
    t.string "confusion_mental_state_changes", limit: 1
    t.string "dazed", limit: 1
    t.string "dizziness", limit: 1
    t.string "focal_neurological_symptoms", limit: 1
    t.string "headache", limit: 1
    t.string "nausea", limit: 1
    t.string "lost_consciousness_under30", limit: 1
    t.string "pta_under24hrs", limit: 1
    t.string "skull_fracture", limit: 1
    t.string "bleeding", limit: 10
    t.string "brusing", limit: 10
    t.string "severe_tbi", limit: 10
    t.string "penetrating_tbi", limit: 1
    t.string "brain_stem_injury", limit: 1
    t.string "multiple_sclerosis", limit: 10
    t.string "stroke", limit: 10
    t.string "substance_history", limit: 10
    t.string "eye_issues", limit: 10
    t.string "opioids", limit: 10
    t.string "chemotherapy", limit: 10
    t.string "radiation", limit: 10
    t.string "bipolar", limit: 10
    t.string "borderline", limit: 10
    t.string "schizo", limit: 10
    t.text "comments"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 10
  end

  create_table "neuro_list_a_z", id: false, force: :cascade do |t|
    t.string "first_name", limit: 20, null: false
    t.string "middle_name", limit: 20
    t.string "last_name", limit: 20
    t.string "suffix", limit: 20, null: false
    t.string "street1", limit: 50, null: false
    t.string "street2", limit: 50
    t.string "street3", limit: 50
    t.string "city", limit: 20, null: false
    t.string "state", limit: 20, null: false
    t.string "zip", limit: 20, null: false
    t.string "county", limit: 30
  end

  create_table "neuro_recruit_final", id: false, force: :cascade do |t|
    t.string "ssn", limit: 12
    t.string "prefix", limit: 10
    t.string "first_name", limit: 200
    t.string "middle_name", limit: 200
    t.string "last_name", limit: 200
    t.string "subject_id", limit: 200
    t.string "diagnosis", limit: 200
    t.string "oef_oif_ond", limit: 200
    t.string "address", limit: 200
    t.string "city", limit: 200
    t.string "state", limit: 200
    t.string "zip", limit: 200
  end

  create_table "neuro_recruited_mg", id: false, force: :cascade do |t|
    t.string "surname", limit: 10
    t.string "first_name", limit: 20, null: false
    t.string "last_name", limit: 20
    t.string "suffix", limit: 20, null: false
    t.string "street1", limit: 50, null: false
    t.string "street2", limit: 50
    t.string "street3", limit: 50
    t.string "city", limit: 20, null: false
    t.string "state", limit: 20, null: false
    t.string "zip", limit: 20, null: false
    t.string "county", limit: 30
  end

  create_table "nih_examiner_dot_counting_score_sheet", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.string "form", limit: 1
    t.bigint "trial_1_correct"
    t.bigint "trial_2_correct"
    t.bigint "trial_3_correct"
    t.bigint "trial_4_correct"
    t.bigint "trial_5_correct"
    t.bigint "trial_6_correct"
    t.bigint "total_correct"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "nih_neuro_qol_cog", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "nih_neuro_qol_em", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "nih_neuro_qol_sa", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "nih_neuro_qol_ss", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "nih_neuro_qol_wb", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "nos", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "oct_iowa_analysis", id: false, force: :cascade do |t|
    t.integer "subject_id"
    t.string "date_of_birth", limit: 10
    t.string "oct_date", limit: 10
    t.string "age_at_visit", limit: 4
    t.string "years_from_baseline_scan", limit: 5
    t.string "mean_rnfl_od", limit: 6
    t.string "mean_gcl_thickness_od", limit: 5
    t.string "mean_rnfl_os", limit: 6
    t.string "mean_gcl_thickness_os", limit: 5
    t.string "visual_field_mean_deviation_od", limit: 5
    t.string "visual_field_pattern_standard_deviation_od", limit: 4
    t.string "visual_field_mean_deviation_os", limit: 5
    t.string "visual_field_pattern_standard_deviation_os", limit: 3
  end

  create_table "pacs_raw", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.integer "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "panss", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "study_id"
    t.bigint "p1"
    t.bigint "p2"
    t.bigint "p3"
    t.bigint "p4"
    t.bigint "p5"
    t.bigint "p6"
    t.bigint "p7"
    t.bigint "n1"
    t.bigint "n2"
    t.bigint "n3"
    t.bigint "n4"
    t.bigint "n5"
    t.bigint "n6"
    t.bigint "n7"
    t.bigint "g1"
    t.bigint "g2"
    t.bigint "g3"
    t.bigint "g4"
    t.bigint "g5"
    t.bigint "g6"
    t.bigint "g7"
    t.bigint "g8"
    t.bigint "g9"
    t.bigint "g10"
    t.bigint "g11"
    t.bigint "g12"
    t.bigint "g13"
    t.bigint "g14"
    t.bigint "g15"
    t.bigint "g16"
    t.bigint "s1"
    t.bigint "s2"
    t.bigint "s3"
    t.string "verified_by", limit: 10
  end

  create_table "pcl_5_raw", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "phq_9", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "qdifficulty"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "phq_9_daily", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "qdifficulty"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "phq_9_weekly", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "qdifficulty"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "procedures", force: :cascade do |t|
    t.string "description", limit: 765, null: false
    t.text "note", null: false
    t.string "created_by", limit: 24, null: false
  end

  create_table "promis_sf6b", force: :cascade do |t|
    t.integer "subject_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "pssqi_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.integer "study_id"
    t.integer "pssqi_1"
    t.string "pssqi_1a", limit: 30
    t.integer "pssqi_2"
    t.string "pssqi_2a", limit: 30
    t.integer "pssqi_3"
    t.string "pssqi_3a", limit: 30
    t.integer "pssqi_4"
    t.string "pssqi_4a", limit: 26
    t.integer "pssqi_5"
    t.string "pssqi_5a", limit: 25
    t.integer "pssqi_6"
    t.integer "pssqi_7"
    t.integer "pssqi_8"
    t.integer "pssqi_9"
    t.integer "pssqi_10"
    t.integer "pssqi_11"
    t.integer "pssqi_12"
    t.integer "pssqi_13"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "pssqi_scored", id: :serial, force: :cascade do |t|
    t.bigint "subject_id", null: false
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "sleep_symptom"
    t.bigint "duration"
    t.bigint "daytime_impairment"
    t.bigint "insomnia_do"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20, null: false
  end

  create_table "qids_sr", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "relapse_query_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.text "explanation"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "session_notes", force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "visit_num"
    t.date "date"
    t.bigint "study_id"
    t.text "notes"
    t.string "administrator", limit: 100
    t.string "verified_by", limit: 11
  end

  create_table "sis_raw", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.string "administrator", limit: 50
    t.string "verified_by", limit: 50
  end

  create_table "staff_training", force: :cascade do |t|
    t.string "first_name", limit: 20, null: false
    t.string "last_name", limit: 20
    t.bigint "study_id"
    t.text "training"
    t.date "training_date"
    t.integer "cleared"
    t.date "expiration_date"
    t.string "trainer", limit: 20
    t.text "comments"
  end

  create_table "state_impulsivity_delay_discounting", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 22
    t.integer "subject"
    t.integer "session"
    t.integer "age"
    t.string "DataFile.Basename", limit: 30
    t.decimal "Display.RefreshRate", precision: 4, scale: 2
    t.string "experimentversion", limit: 9
    t.string "group", limit: 4
    t.integer "randomseed"
    t.string "runtimecapabilities", limit: 12
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 7
    t.string "studioversion", limit: 10
    t.integer "block"
    t.string "Condition[Block]", limit: 11
    t.string "experimentlist", limit: 1
    t.string "ExperimentList.Cycle", limit: 1
    t.string "ExperimentList.Sample", limit: 1
    t.string "increment", limit: 2
    t.string "initialpracticelist", limit: 1
    t.string "InitialPracticeList.Cycle", limit: 1
    t.string "InitialPracticeList.Sample", limit: 1
    t.string "introlist", limit: 1
    t.string "IntroList.Cycle", limit: 1
    t.string "IntroList.Sample", limit: 1
    t.string "MaxBottom[Block]", limit: 1
    t.string "MaxTop[Block]", limit: 4
    t.string "MinBottom[Block]", limit: 1
    t.string "MinTop[Block]", limit: 4
    t.string "PracticeSlide.ACC", limit: 1
    t.string "PracticeSlide.CRESP", limit: 10
    t.string "PracticeSlide.RESP", limit: 1
    t.string "PracticeSlide.RT", limit: 4
    t.string "PracticeSlide.RTTime", limit: 6
    t.string "Procedure[Block]", limit: 14
    t.string "Running[Block]", limit: 19
    t.string "secondpracticelist", limit: 1
    t.string "SecondPracticeList.Cycle", limit: 1
    t.string "SecondPracticeList.Sample", limit: 1
    t.string "standard", limit: 7
    t.string "strFirstChoice[Block]", limit: 14
    t.string "strSecondChoice[Block]", limit: 24
    t.string "validchoice", limit: 8
    t.string "Value[Block]", limit: 3
    t.string "VariableAmount[Block]", limit: 7
    t.string "waittime", limit: 1
    t.string "trial", limit: 1
    t.string "Condition[Trial]", limit: 5
    t.string "condlist", limit: 1
    t.string "CondList.Cycle", limit: 1
    t.string "CondList.Sample", limit: 1
    t.string "Procedure[Trial]", limit: 8
    t.string "Running[Trial]", limit: 8
    t.string "Value[Trial]", limit: 1
    t.string "subtrial", limit: 3
    t.string "firstblocklist", limit: 1
    t.string "FirstBlockList.Cycle", limit: 1
    t.string "FirstBlockList.Sample", limit: 2
    t.string "Procedure[SubTrial]", limit: 14
    t.string "Running[SubTrial]", limit: 15
    t.string "secondblocklist", limit: 1
    t.string "SecondBlockList.Cycle", limit: 2
    t.string "SecondBlockList.Sample", limit: 2
    t.string "loglevel5", limit: 1
    t.string "adjustedmaxbottom", limit: 8
    t.string "adjustedmaxtop", limit: 10
    t.string "adjustedminbottom", limit: 8
    t.string "adjustedmintop", limit: 10
    t.string "choice", limit: 8
    t.string "ChoiceSlide.ACC", limit: 1
    t.string "ChoiceSlide.CRESP", limit: 10
    t.string "ChoiceSlide.RESP", limit: 1
    t.string "ChoiceSlide.RT", limit: 6
    t.string "ChoiceSlide.RTTime", limit: 7
    t.string "Condition[LogLevel5]", limit: 11
    t.string "condnum", limit: 2
    t.string "difference", limit: 5
    t.string "MaxBottom[LogLevel5]", limit: 8
    t.string "MaxTop[LogLevel5]", limit: 10
    t.string "MinBottom[LogLevel5]", limit: 8
    t.string "MinTop[LogLevel5]", limit: 10
    t.string "newtriallist", limit: 1
    t.string "NewTrialList.Cycle", limit: 2
    t.string "NewTrialList.Sample", limit: 2
    t.string "Procedure[LogLevel5]", limit: 15
    t.string "randomlist", limit: 1
    t.string "RandomList.Cycle", limit: 2
    t.string "RandomList.Sample", limit: 2
    t.string "Running[LogLevel5]", limit: 12
    t.string "strFirstChoice[LogLevel5]", limit: 24
    t.string "strSecondChoice[LogLevel5]", limit: 24
    t.string "triallist", limit: 1
    t.string "TrialList.Cycle", limit: 3
    t.string "TrialList.Sample", limit: 2
    t.string "trialnum", limit: 3
    t.string "Value[LogLevel5]", limit: 3
    t.string "VariableAmount[LogLevel5]", limit: 10
  end

  create_table "state_impulsivity_risk_task_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 14
    t.integer "subject"
    t.integer "session"
    t.string "DataFile.Basename", limit: 22
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 9
    t.integer "group"
    t.integer "randomseed"
    t.string "runtimecapabilities", limit: 12
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 7
    t.string "studioversion", limit: 10
    t.integer "block"
    t.integer "blocklist"
    t.integer "BlockList.Cycle"
    t.integer "BlockList.Sample"
    t.string "practicemode", limit: 2
    t.string "Procedure[Block]", limit: 9
    t.string "Running[Block]", limit: 9
    t.integer "trial"
    t.integer "blueanswerbox"
    t.string "bluebox", limit: 11
    t.string "box1", limit: 15
    t.string "box2", limit: 15
    t.string "box3", limit: 15
    t.string "box4", limit: 15
    t.string "box5", limit: 15
    t.string "box6", limit: 11
    t.string "boxratio", limit: 9
    t.integer "correctanswer"
    t.integer "l"
    t.integer "picturelist"
    t.string "Procedure[Trial]", limit: 9
    t.integer "redanswerbox"
    t.string "redbox", limit: 15
    t.string "Running[Trial]", limit: 9
    t.integer "Slide1.ACC"
    t.integer "Slide1.CRESP"
    t.integer "Slide1.FinishTime"
    t.integer "Slide1.RESP"
    t.integer "Slide1.RT"
    t.integer "Slide1.StartTime"
    t.integer "startvalue"
    t.string "token", limit: 15
    t.string "tokenbox1", limit: 15
    t.string "tokenbox2", limit: 15
    t.string "tokenbox3", limit: 15
    t.string "tokenbox4", limit: 15
    t.string "tokenbox5", limit: 15
    t.string "tokenbox6", limit: 15
    t.integer "totalsum"
    t.integer "trialcount"
    t.integer "triallist"
    t.integer "TrialList.Cycle"
    t.integer "TrialList.Sample"
    t.integer "var"
    t.integer "w"
  end

  create_table "state_impulsivity_stop_signal", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 14
    t.integer "subject"
    t.integer "session"
    t.string "DataFile.Basename", limit: 22
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 8
    t.integer "group"
    t.integer "randomseed"
    t.string "runtimecapabilities", limit: 4
    t.string "runtimeversion", limit: 8
    t.string "runtimeversionexpected", limit: 8
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 8
    t.string "studioversion", limit: 8
    t.string "Welcome.DEVICE", limit: 8
    t.integer "Welcome.DurationError"
    t.integer "Welcome.OnsetDelay"
    t.integer "Welcome.OnsetTime"
    t.integer "Welcome.OnsetToOnsetTime"
    t.integer "block"
    t.string "BlockInstructions.DEVICE", limit: 8
    t.string "BlockInstructions.DurationError", limit: 7
    t.string "BlockInstructions.OnsetDelay", limit: 2
    t.string "BlockInstructions.OnsetTime", limit: 5
    t.string "BlockInstructions.OnsetToOnsetTime", limit: 1
    t.integer "blocklist"
    t.integer "BlockList.Cycle"
    t.integer "BlockList.Sample"
    t.string "EndPrac.DEVICE", limit: 8
    t.string "EndPrac.DurationError", limit: 7
    t.string "EndPrac.OnsetDelay", limit: 2
    t.string "EndPrac.OnsetTime", limit: 5
    t.string "EndPrac.OnsetToOnsetTime", limit: 1
    t.integer "GetReady.DurationError"
    t.integer "GetReady.OnsetDelay"
    t.integer "GetReady.OnsetTime"
    t.integer "GetReady.OnsetToOnsetTime"
    t.string "PracInstructions.DEVICE", limit: 8
    t.string "PracInstructions.DurationError", limit: 7
    t.string "PracInstructions.OnsetDelay", limit: 2
    t.string "PracInstructions.OnsetTime", limit: 5
    t.string "PracInstructions.OnsetToOnsetTime", limit: 1
    t.string "pracrtaverage", limit: 3
    t.string "Procedure[Block]", limit: 13
    t.string "Running[Block]", limit: 9
    t.integer "trial"
    t.string "correctresponse", limit: 1
    t.string "Feedback.DurationError", limit: 1
    t.string "Feedback.OnsetDelay", limit: 2
    t.string "Feedback.OnsetTime", limit: 5
    t.string "Feedback.OnsetToOnsetTime", limit: 1
    t.string "feedbackstate", limit: 9
    t.integer "Fixation.DurationError"
    t.integer "Fixation.OnsetDelay"
    t.integer "Fixation.OnsetTime"
    t.integer "Fixation.OnsetToOnsetTime"
    t.string "practriallist", limit: 2
    t.string "PracTrialList.Cycle", limit: 1
    t.string "PracTrialList.Sample", limit: 2
    t.string "Procedure[Trial]", limit: 13
    t.string "Running[Trial]", limit: 13
    t.integer "StimDisplay.ACC"
    t.string "StimDisplay.CRESP", limit: 1
    t.string "StimDisplay.DEVICE", limit: 8
    t.integer "StimDisplay.DurationError"
    t.integer "StimDisplay.OnsetDelay"
    t.integer "StimDisplay.OnsetTime"
    t.integer "StimDisplay.OnsetToOnsetTime"
    t.string "StimDisplay.RESP", limit: 1
    t.integer "StimDisplay.RT"
    t.integer "StimDisplay.RTTime"
    t.string "stimimage", limit: 18
    t.string "tasktype", limit: 10
    t.string "TrialFeedback.DurationError", limit: 1
    t.string "TrialFeedback.OnsetDelay", limit: 2
    t.string "TrialFeedback.OnsetTime", limit: 6
    t.string "TrialFeedback.OnsetToOnsetTime", limit: 1
    t.string "triallist", limit: 3
    t.string "TrialList.Cycle", limit: 1
    t.string "TrialList.Sample", limit: 3
  end

  create_table "state_impulsivity_stroop", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 6
    t.integer "subject"
    t.integer "session"
    t.string "DataFile.Basename", limit: 14
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 8
    t.integer "group"
    t.string "Instructions.DEVICE", limit: 8
    t.bigint "randomseed"
    t.string "runtimecapabilities", limit: 4
    t.string "runtimeversion", limit: 8
    t.string "runtimeversionexpected", limit: 8
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 7
    t.string "studioversion", limit: 8
    t.integer "block"
    t.integer "blocklist"
    t.integer "BlockList.Cycle"
    t.integer "BlockList.Sample"
    t.string "practicemode", limit: 3
    t.string "Procedure[Block]", limit: 13
    t.string "Running[Block]", limit: 9
    t.integer "trial"
    t.integer "colorlist"
    t.string "congruency", limit: 11
    t.string "correct", limit: 1
    t.string "practriallist", limit: 1
    t.string "PracTrialList.Cycle", limit: 1
    t.string "PracTrialList.Sample", limit: 1
    t.string "Procedure[Trial]", limit: 9
    t.string "Running[Trial]", limit: 13
    t.string "stimcolor", limit: 6
    t.integer "Stimulus.ACC"
    t.string "Stimulus.CRESP", limit: 1
    t.string "Stimulus.DEVICE", limit: 8
    t.integer "Stimulus.DurationError"
    t.integer "Stimulus.OnsetDelay"
    t.integer "Stimulus.OnsetTime"
    t.integer "Stimulus.OnsetToOnsetTime"
    t.string "Stimulus.RESP", limit: 1
    t.integer "Stimulus.RT"
    t.integer "Stimulus.RTTime"
    t.string "stimword", limit: 6
    t.string "triallist", limit: 1
    t.string "TrialList.Cycle", limit: 2
    t.string "TrialList.Sample", limit: 3
  end

  create_table "studies", force: :cascade do |t|
    t.string "irb_number", limit: 25
    t.string "description", limit: 25
    t.text "note"
    t.string "investigator", limit: 20
    t.bigint "status"
    t.date "start_date"
    t.date "end_date"
    t.string "created_by", limit: 20
  end

  create_table "subject_binders_inventory", force: :cascade do |t|
    t.bigint "study"
    t.string "room", limit: 10
    t.text "location"
    t.string "created_by", limit: 10
  end

  create_table "tass", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "tdcs_symptom_ratings", force: :cascade do |t|
    t.bigint "subject_id"
    t.string "event_id", limit: 11
    t.date "date"
    t.time "time"
    t.integer "study_id"
    t.integer "pre_post"
    t.integer "visit_num"
    t.integer "page_link"
    t.bigint "headache_severity"
    t.bigint "neck_pain_severity"
    t.bigint "scalp_pain_severity"
    t.bigint "tingling_severity"
    t.bigint "itching_severity"
    t.bigint "burning_severity"
    t.bigint "skin_redness_severity"
    t.bigint "sleepiness_severity"
    t.bigint "concentration_severity"
    t.bigint "mood_change_severity"
    t.bigint "nauseau_severity"
    t.text "other_symptom"
    t.bigint "other_severity"
    t.text "administrator"
    t.string "time_stamp", limit: 30
    t.string "verified_by", limit: 10
  end

  create_table "technology_inventory", force: :cascade do |t|
    t.bigint "labidnumber"
    t.string "itemdescription", limit: 200
    t.string "itembrand", limit: 200
    t.string "itemserialnumber", limit: 200
    t.string "itemroom", limit: 50
    t.text "itemlocation"
    t.date "createddate"
    t.string "createdby", limit: 50
    t.date "updateddate"
    t.string "updatedby", limit: 50
  end

  create_table "tms_aud_delay_discounting_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 22
    t.integer "subject"
    t.integer "session"
    t.integer "age"
    t.string "DataFile.Basename", limit: 29
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 8
    t.string "group", limit: 4
    t.bigint "randomseed"
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 7
    t.string "studioversion", limit: 10
    t.integer "block"
    t.string "Condition[Block]", limit: 11
    t.string "experimentlist", limit: 1
    t.string "ExperimentList.Cycle", limit: 1
    t.string "ExperimentList.Sample", limit: 1
    t.string "increment", limit: 2
    t.string "initialpracticelist", limit: 1
    t.string "InitialPracticeList.Cycle", limit: 1
    t.string "InitialPracticeList.Sample", limit: 1
    t.string "introlist", limit: 1
    t.string "IntroList.Cycle", limit: 1
    t.string "IntroList.Sample", limit: 1
    t.string "MaxBottom[Block]", limit: 1
    t.string "MaxTop[Block]", limit: 4
    t.string "MinBottom[Block]", limit: 1
    t.string "MinTop[Block]", limit: 4
    t.string "PracticeSlide.ACC", limit: 1
    t.string "PracticeSlide.CRESP", limit: 10
    t.string "PracticeSlide.RESP", limit: 1
    t.string "PracticeSlide.RT", limit: 4
    t.string "PracticeSlide.RTTime", limit: 6
    t.string "Procedure[Block]", limit: 14
    t.string "Running[Block]", limit: 19
    t.string "secondpracticelist", limit: 1
    t.string "SecondPracticeList.Cycle", limit: 1
    t.string "SecondPracticeList.Sample", limit: 1
    t.string "standard", limit: 7
    t.string "strFirstChoice[Block]", limit: 14
    t.string "strSecondChoice[Block]", limit: 24
    t.string "validchoice", limit: 8
    t.string "Value[Block]", limit: 3
    t.string "VariableAmount[Block]", limit: 7
    t.string "waittime", limit: 2
    t.string "trial", limit: 1
    t.string "Condition[Trial]", limit: 5
    t.string "condlist", limit: 1
    t.string "CondList.Cycle", limit: 1
    t.string "CondList.Sample", limit: 1
    t.string "Procedure[Trial]", limit: 8
    t.string "Running[Trial]", limit: 8
    t.string "Value[Trial]", limit: 1
    t.string "subtrial", limit: 3
    t.string "firstblocklist", limit: 1
    t.string "FirstBlockList.Cycle", limit: 1
    t.string "FirstBlockList.Sample", limit: 2
    t.string "Procedure[SubTrial]", limit: 14
    t.string "Running[SubTrial]", limit: 15
    t.string "secondblocklist", limit: 1
    t.string "SecondBlockList.Cycle", limit: 2
    t.string "SecondBlockList.Sample", limit: 2
    t.string "loglevel5", limit: 1
    t.string "adjustedmaxbottom", limit: 8
    t.string "adjustedmaxtop", limit: 10
    t.string "adjustedminbottom", limit: 8
    t.string "adjustedmintop", limit: 10
    t.string "choice", limit: 8
    t.string "ChoiceSlide.ACC", limit: 1
    t.string "ChoiceSlide.CRESP", limit: 10
    t.string "ChoiceSlide.RESP", limit: 1
    t.string "ChoiceSlide.RT", limit: 5
    t.string "ChoiceSlide.RTTime", limit: 6
    t.string "Condition[LogLevel5]", limit: 11
    t.string "condnum", limit: 2
    t.string "difference", limit: 5
    t.string "MaxBottom[LogLevel5]", limit: 8
    t.string "MaxTop[LogLevel5]", limit: 10
    t.string "MinBottom[LogLevel5]", limit: 8
    t.string "MinTop[LogLevel5]", limit: 10
    t.string "newtriallist", limit: 1
    t.string "NewTrialList.Cycle", limit: 2
    t.string "NewTrialList.Sample", limit: 2
    t.string "Procedure[LogLevel5]", limit: 15
    t.string "randomlist", limit: 1
    t.string "RandomList.Cycle", limit: 2
    t.string "RandomList.Sample", limit: 2
    t.string "Running[LogLevel5]", limit: 12
    t.string "strFirstChoice[LogLevel5]", limit: 24
    t.string "strSecondChoice[LogLevel5]", limit: 24
    t.string "triallist", limit: 1
    t.string "TrialList.Cycle", limit: 3
    t.string "TrialList.Sample", limit: 2
    t.string "trialnum", limit: 3
    t.string "Value[LogLevel5]", limit: 3
    t.string "VariableAmount[LogLevel5]", limit: 8
  end

  create_table "tms_aud_nih_examiner_flanker", id: false, force: :cascade do |t|
    t.string "task_name", limit: 7
    t.string "task_version", limit: 7
    t.string "task_versiondate", limit: 10
    t.string "task_form", limit: 1
    t.string "task_agecohort", limit: 5
    t.string "task_language", limit: 7
    t.string "site_id", limit: 14
    t.integer "subject_id"
    t.integer "session_num"
    t.string "session_date", limit: 10
    t.string "session_start", limit: 5
    t.string "initials", limit: 3
    t.string "machine_id", limit: 12
    t.string "response_device", limit: 8
    t.string "block_name", limit: 19
    t.integer "trial_congruent"
    t.string "trial_arrows", limit: 5
    t.string "trial_updown", limit: 4
    t.string "trial_corrresp", limit: 5
    t.decimal "trial_fixation", precision: 4, scale: 3
    t.string "resp_value", limit: 5
    t.integer "resp_corr"
    t.decimal "resp_rt", precision: 8, scale: 7
    t.decimal "task_time", precision: 10, scale: 7
  end

  create_table "tms_aud_nih_examiner_flanker_summary", id: false, force: :cascade do |t|
    t.string "task_name", limit: 7
    t.string "task_version", limit: 7
    t.string "task_versiondate", limit: 10
    t.string "task_form", limit: 1
    t.string "task_agecohort", limit: 5
    t.string "task_language", limit: 7
    t.string "site_id", limit: 14
    t.integer "subject_id"
    t.integer "session_num"
    t.string "session_date", limit: 10
    t.string "session_start", limit: 5
    t.string "initials", limit: 3
    t.string "machine_id", limit: 12
    t.string "response_device", limit: 8
    t.integer "total_trials"
    t.decimal "flanker_score", precision: 4, scale: 3
    t.integer "flanker_error_diff"
    t.integer "total_corr"
    t.decimal "total_mean", precision: 5, scale: 4
    t.decimal "total_median", precision: 5, scale: 4
    t.decimal "total_stdev", precision: 5, scale: 4
    t.integer "congr_corr"
    t.decimal "congr_mean", precision: 5, scale: 4
    t.decimal "congr_median", precision: 5, scale: 4
    t.decimal "congr_stdev", precision: 5, scale: 4
    t.integer "incongr_corr"
    t.decimal "incongr_mean", precision: 5, scale: 4
    t.decimal "incongr_median", precision: 5, scale: 4
    t.decimal "incongr_stdev", precision: 5, scale: 4
    t.integer "left_corr"
    t.decimal "left_mean", precision: 5, scale: 4
    t.decimal "left_median", precision: 5, scale: 4
    t.decimal "left_stdev", precision: 5, scale: 4
    t.integer "right_corr"
    t.decimal "right_mean", precision: 5, scale: 4
    t.decimal "right_median", precision: 5, scale: 4
    t.decimal "right_stdev", precision: 5, scale: 4
    t.integer "up_corr"
    t.decimal "up_mean", precision: 5, scale: 4
    t.decimal "up_median", precision: 4, scale: 3
    t.decimal "up_stdev", precision: 2, scale: 1
    t.integer "down_corr"
    t.decimal "down_mean", precision: 5, scale: 4
    t.decimal "down_median", precision: 5, scale: 4
    t.decimal "down_stdev", precision: 4, scale: 3
  end

  create_table "tms_aud_nih_examiner_nback", id: false, force: :cascade do |t|
    t.string "task_name", limit: 5
    t.string "task_version", limit: 7
    t.string "task_versiondate", limit: 10
    t.string "task_form", limit: 1
    t.string "task_agecohort", limit: 5
    t.string "task_language", limit: 7
    t.string "site_id", limit: 14
    t.integer "subject_id"
    t.integer "session_num"
    t.string "session_date", limit: 10
    t.string "session_start", limit: 5
    t.string "initials", limit: 3
    t.string "machine_id", limit: 12
    t.string "response_device", limit: 8
    t.string "block_name", limit: 17
    t.integer "trial_number"
    t.integer "trial_location"
    t.string "trial_similarity", limit: 1
    t.string "trial_corr_resp", limit: 5
    t.string "trial_visual_hemi", limit: 1
    t.string "trial_interference", limit: 1
    t.string "resp_value", limit: 5
    t.integer "resp_corr"
    t.decimal "resp_rt", precision: 8, scale: 7
    t.decimal "task_time", precision: 10, scale: 7
  end

  create_table "tms_aud_nih_examiner_nback_summary", id: false, force: :cascade do |t|
    t.string "task_name", limit: 5
    t.string "task_version", limit: 7
    t.string "task_versiondate", limit: 10
    t.string "task_form", limit: 1
    t.string "task_agecohort", limit: 5
    t.string "task_language", limit: 7
    t.string "site_id", limit: 14
    t.integer "subject_id"
    t.integer "session_num"
    t.string "session_date", limit: 10
    t.string "session_start", limit: 5
    t.string "initials", limit: 3
    t.string "machine_id", limit: 12
    t.string "response_device", limit: 8
    t.integer "nb1_total_trials"
    t.decimal "nb1_score", precision: 4, scale: 3
    t.decimal "nb1_bias", precision: 4, scale: 3
    t.integer "nb1_corr"
    t.integer "nb1_errors"
    t.decimal "nb1_mean", precision: 5, scale: 4
    t.decimal "nb1_median", precision: 5, scale: 4
    t.decimal "nb1_stdev", precision: 5, scale: 4
    t.integer "nb1sm_corr"
    t.integer "nb1sm_errors"
    t.decimal "nb1sm_mean", precision: 5, scale: 4
    t.decimal "nb1sm_median", precision: 5, scale: 4
    t.decimal "nb1sm_stdev", precision: 5, scale: 4
    t.integer "nb1s1_corr"
    t.integer "nb1s1_errors"
    t.decimal "nb1s1_mean", precision: 5, scale: 4
    t.decimal "nb1s1_median", precision: 5, scale: 4
    t.decimal "nb1s1_stdev", precision: 5, scale: 4
    t.integer "nb1s2_corr"
    t.integer "nb1s2_errors"
    t.decimal "nb1s2_mean", precision: 5, scale: 4
    t.decimal "nb1s2_median", precision: 5, scale: 4
    t.decimal "nb1s2_stdev", precision: 5, scale: 4
    t.integer "nb1s3_corr"
    t.integer "nb1s3_errors"
    t.decimal "nb1s3_mean", precision: 5, scale: 4
    t.decimal "nb1s3_median", precision: 5, scale: 4
    t.decimal "nb1s3_stdev", precision: 5, scale: 4
    t.integer "nb1s4_corr"
    t.integer "nb1s4_errors"
    t.decimal "nb1s4_mean", precision: 5, scale: 4
    t.decimal "nb1s4_median", precision: 5, scale: 4
    t.decimal "nb1s4_stdev", precision: 5, scale: 4
    t.integer "nb1vhl_corr"
    t.integer "nb1vhl_errors"
    t.decimal "nb1vhl_mean", precision: 5, scale: 4
    t.decimal "nb1vhl_median", precision: 5, scale: 4
    t.decimal "nb1vhl_stdev", precision: 5, scale: 4
    t.integer "nb1vhr_corr"
    t.integer "nb1vhr_errors"
    t.decimal "nb1vhr_mean", precision: 5, scale: 4
    t.decimal "nb1vhr_median", precision: 5, scale: 4
    t.decimal "nb1vhr_stdev", precision: 5, scale: 4
    t.integer "nb2_total_trials"
    t.decimal "nb2_score", precision: 4, scale: 3
    t.decimal "nb2_bias", precision: 4, scale: 3
    t.integer "nb2_corr"
    t.integer "nb2_errors"
    t.decimal "nb2_mean", precision: 5, scale: 4
    t.decimal "nb2_median", precision: 5, scale: 4
    t.decimal "nb2_stdev", precision: 4, scale: 3
    t.integer "nb2sm_corr"
    t.integer "nb2sm_errors"
    t.decimal "nb2sm_mean", precision: 5, scale: 4
    t.decimal "nb2sm_median", precision: 5, scale: 4
    t.decimal "nb2sm_stdev", precision: 4, scale: 3
    t.integer "nb2s1_corr"
    t.integer "nb2s1_errors"
    t.decimal "nb2s1_mean", precision: 5, scale: 4
    t.decimal "nb2s1_median", precision: 5, scale: 4
    t.decimal "nb2s1_stdev", precision: 5, scale: 4
    t.integer "nb2s2_corr"
    t.integer "nb2s2_errors"
    t.decimal "nb2s2_mean", precision: 5, scale: 4
    t.decimal "nb2s2_median", precision: 5, scale: 4
    t.decimal "nb2s2_stdev", precision: 5, scale: 4
    t.integer "nb2s3_corr"
    t.integer "nb2s3_errors"
    t.decimal "nb2s3_mean", precision: 4, scale: 3
    t.decimal "nb2s3_median", precision: 5, scale: 4
    t.decimal "nb2s3_stdev", precision: 5, scale: 4
    t.integer "nb2s4_corr"
    t.integer "nb2s4_errors"
    t.decimal "nb2s4_mean", precision: 5, scale: 4
    t.decimal "nb2s4_median", precision: 5, scale: 4
    t.decimal "nb2s4_stdev", precision: 5, scale: 4
    t.integer "nb2vhl_corr"
    t.integer "nb2vhl_errors"
    t.decimal "nb2vhl_mean", precision: 5, scale: 4
    t.decimal "nb2vhl_median", precision: 5, scale: 4
    t.decimal "nb2vhl_stdev", precision: 5, scale: 4
    t.integer "nb2vhr_corr"
    t.integer "nb2vhr_errors"
    t.decimal "nb2vhr_mean", precision: 5, scale: 4
    t.decimal "nb2vhr_median", precision: 5, scale: 4
    t.decimal "nb2vhr_stdev", precision: 5, scale: 4
    t.integer "nb2int_corr"
    t.integer "nb2int_errors"
    t.decimal "nb2int_mean", precision: 5, scale: 4
    t.decimal "nb2int_median", precision: 5, scale: 4
    t.decimal "nb2int_stdev", precision: 4, scale: 3
    t.integer "nb2noint_corr"
    t.integer "nb2noint_errors"
    t.decimal "nb2noint_mean", precision: 5, scale: 4
    t.decimal "nb2noint_median", precision: 5, scale: 4
    t.decimal "nb2noint_stdev", precision: 5, scale: 4
  end

  create_table "tms_aud_risk_task_raw", id: false, force: :cascade do |t|
    t.string "experimentname", limit: 14
    t.integer "subject"
    t.integer "session"
    t.string "DataFile.Basename", limit: 23
    t.decimal "Display.RefreshRate", precision: 5, scale: 3
    t.string "experimentversion", limit: 8
    t.integer "group"
    t.integer "randomseed"
    t.string "runtimeversion", limit: 10
    t.string "runtimeversionexpected", limit: 10
    t.string "sessiondate", limit: 10
    t.string "sessionstartdatetimeutc", limit: 15
    t.string "sessiontime", limit: 8
    t.string "studioversion", limit: 10
    t.integer "block"
    t.integer "blocklist"
    t.integer "BlockList.Cycle"
    t.integer "BlockList.Sample"
    t.string "practicemode", limit: 2
    t.string "Procedure[Block]", limit: 9
    t.string "Running[Block]", limit: 9
    t.integer "trial"
    t.integer "blueanswerbox"
    t.string "bluebox", limit: 11
    t.string "box1", limit: 15
    t.string "box2", limit: 15
    t.string "box3", limit: 15
    t.string "box4", limit: 15
    t.string "box5", limit: 15
    t.string "box6", limit: 11
    t.string "boxratio", limit: 9
    t.integer "correctanswer"
    t.integer "l"
    t.integer "picturelist"
    t.string "Procedure[Trial]", limit: 9
    t.integer "redanswerbox"
    t.string "redbox", limit: 15
    t.string "Running[Trial]", limit: 9
    t.integer "Slide1.ACC"
    t.integer "Slide1.CRESP"
    t.integer "Slide1.FinishTime"
    t.integer "Slide1.RESP"
    t.integer "Slide1.RT"
    t.integer "Slide1.StartTime"
    t.integer "startvalue"
    t.string "token", limit: 15
    t.string "tokenbox1", limit: 15
    t.string "tokenbox2", limit: 15
    t.string "tokenbox3", limit: 15
    t.string "tokenbox4", limit: 15
    t.string "tokenbox5", limit: 15
    t.string "tokenbox6", limit: 15
    t.integer "totalsum"
    t.integer "trialcount"
    t.integer "triallist"
    t.integer "TrialList.Cycle"
    t.integer "TrialList.Sample"
    t.integer "var"
    t.integer "w"
  end

  create_table "trail_making_test", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.string "trail_a", limit: 11
    t.string "trail_b", limit: 11
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "tss", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.text "comments"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "upps_raw", id: :serial, force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "event_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.decimal "upps_1", precision: 1
    t.decimal "upps_2", precision: 1
    t.decimal "upps_3", precision: 1
    t.decimal "upps_4", precision: 1
    t.decimal "upps_5", precision: 1
    t.decimal "upps_6", precision: 1
    t.decimal "upps_7", precision: 1
    t.decimal "upps_8", precision: 1
    t.decimal "upps_9", precision: 1
    t.decimal "upps_10", precision: 1
    t.decimal "upps_11", precision: 1
    t.decimal "upps_12", precision: 1
    t.decimal "upps_13", precision: 1
    t.decimal "upps_14", precision: 1
    t.decimal "upps_15", precision: 1
    t.decimal "upps_16", precision: 1
    t.decimal "upps_17", precision: 1
    t.decimal "upps_18", precision: 1
    t.decimal "upps_19", precision: 1
    t.decimal "upps_20", precision: 1
    t.decimal "upps_21", precision: 1
    t.decimal "upps_22", precision: 1
    t.decimal "upps_23", precision: 1
    t.decimal "upps_24", precision: 1
    t.decimal "upps_25", precision: 1
    t.decimal "upps_26", precision: 1
    t.decimal "upps_27", precision: 1
    t.decimal "upps_28", precision: 1
    t.decimal "upps_29", precision: 1
    t.decimal "upps_30", precision: 1
    t.decimal "upps_31", precision: 1
    t.decimal "upps_32", precision: 1
    t.decimal "upps_33", precision: 1
    t.decimal "upps_34", precision: 1
    t.decimal "upps_35", precision: 1
    t.decimal "upps_36", precision: 1
    t.decimal "upps_37", precision: 1
    t.decimal "upps_38", precision: 1
    t.decimal "upps_39", precision: 1
    t.decimal "upps_40", precision: 1
    t.decimal "upps_41", precision: 1
    t.decimal "upps_42", precision: 1
    t.decimal "upps_43", precision: 1
    t.decimal "upps_44", precision: 1
    t.decimal "upps_45", precision: 1
    t.decimal "upps_46", precision: 1
    t.decimal "upps_47", precision: 1
    t.decimal "upps_48", precision: 1
    t.decimal "upps_49", precision: 1
    t.decimal "upps_50", precision: 1
    t.decimal "upps_51", precision: 1
    t.decimal "upps_52", precision: 1
    t.decimal "upps_53", precision: 1
    t.decimal "upps_54", precision: 1
    t.decimal "upps_55", precision: 1
    t.decimal "upps_56", precision: 1
    t.decimal "upps_57", precision: 1
    t.decimal "upps_58", precision: 1
    t.decimal "upps_59", precision: 1
    t.text "administrator"
    t.string "verified_by", limit: 30, null: false
  end

  create_table "upps_scored", id: false, force: :cascade do |t|
    t.bigint "id"
    t.bigint "subject_id"
    t.bigint "event_id"
    t.string "date", limit: 255
    t.bigint "visit_num"
    t.bigint "study_id"
    t.string "administrator", limit: 255
    t.string "verified_by", limit: 255
    t.float "negative_urgency"
    t.float "positive_urgency"
    t.float "premeditation"
    t.float "perseverance"
    t.float "sensation_seeking"
    t.float "total_score"
  end

  create_table "vfq_25", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.bigint "q1"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4"
    t.bigint "q5"
    t.bigint "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.bigint "q12"
    t.bigint "q13"
    t.bigint "q14"
    t.bigint "q15"
    t.bigint "q15a"
    t.bigint "q15b"
    t.bigint "q15c"
    t.bigint "q16"
    t.bigint "q16a"
    t.bigint "q17"
    t.bigint "q18"
    t.bigint "q19"
    t.bigint "q20"
    t.bigint "q21"
    t.bigint "q22"
    t.bigint "q23"
    t.bigint "q24"
    t.bigint "q25"
    t.bigint "qa1"
    t.bigint "qa2"
    t.bigint "qa3"
    t.bigint "qa4"
    t.bigint "qa5"
    t.bigint "qa6"
    t.bigint "qa7"
    t.bigint "qa8"
    t.bigint "qa9"
    t.bigint "qa11a"
    t.bigint "qa11b"
    t.bigint "qa12"
    t.bigint "qa13"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "vision_assessments", force: :cascade do |t|
    t.bigint "subject_id"
    t.bigint "visit_num"
    t.date "date"
    t.bigint "study_id"
    t.bigint "sex"
    t.date "date_of_birth"
    t.bigint "q1"
    t.bigint "q1a"
    t.bigint "q2"
    t.bigint "q3"
    t.bigint "q4_spectralis"
    t.text "q4_spectralis_comments"
    t.bigint "q5_cirrus"
    t.text "q5_cirrus_comments"
    t.bigint "q6_lsfg"
    t.text "q6_lsfg_comments"
    t.bigint "q7_acuity"
    t.text "q7_acuity_comments"
    t.bigint "q8_contrast"
    t.text "q8_contrast_comments"
    t.bigint "q9_vf"
    t.text "q9_vf_comments"
    t.bigint "q10_pupil"
    t.text "q10_pupil_comments"
    t.bigint "q11_hitt"
    t.text "q11_hitt_comments"
    t.text "comments"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

  create_table "vision_history", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "study_id"
    t.integer "q1_diabetes"
    t.string "q1a_diabetes_type", limit: 1
    t.integer "q2_astigmatism"
    t.integer "q3_hyperopia"
    t.integer "q4_myopia"
    t.integer "q5_vision_externally_corrected"
    t.string "q5a_type_worn", limit: 10
    t.string "q5b_prescription_od", limit: 30
    t.string "q5c_prescription_os", limit: 30
    t.integer "q6_vision_correction_surgery"
    t.integer "q7_photophobia"
    t.integer "q8_vitreousdetachment_floaters"
    t.integer "q9_cataracts_nuclearsclerosis"
    t.integer "q10_pseudophakia"
    t.integer "Q11_corneal scar"
    t.integer "q12_retinal_tear"
    t.integer "q13_corneal_dystrophy"
    t.string "q14_amblyopia_lazyeye", limit: 10
    t.string "q14a_eye", limit: 10
    t.integer "q15_other_significant_eye_conditions"
    t.text "q15a_description"
    t.integer "q16_significant_eye_trauma"
    t.text "q16a_description"
    t.string "q17_last_eye_exam", limit: 11
    t.date "q17a_lee_date"
    t.string "q17b_lee_location", limit: 30
    t.string "administrator", limit: 20
    t.string "cprs_review_by", limit: 10
    t.date "cprs_review_date"
    t.text "cprs_discrepancies"
    t.string "verified_by", limit: 10
  end

  create_table "visual_acuity", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "study_id"
    t.bigint "#_correct"
    t.text "score"
    t.string "eye_recorded", limit: 20
    t.bigint "luminance"
    t.bigint "glare"
    t.string "correction", limit: 20
    t.string "examiner", limit: 30
    t.text "test_comments"
    t.text "raw_data"
    t.string "verified_by", limit: 20
  end

  create_table "whoqol_bref_raw", force: :cascade do |t|
    t.integer "subject_id"
    t.date "date"
    t.integer "visit_num"
    t.integer "study_id"
    t.integer "q1"
    t.integer "q2"
    t.integer "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.integer "q7"
    t.integer "q8"
    t.integer "q9"
    t.integer "q10"
    t.integer "q11"
    t.integer "q12"
    t.integer "q13"
    t.integer "q14"
    t.integer "q15"
    t.integer "q16"
    t.integer "q17"
    t.integer "q18"
    t.integer "q19"
    t.integer "q20"
    t.integer "q21"
    t.integer "q22"
    t.integer "q23"
    t.integer "q24"
    t.integer "q25"
    t.integer "q26"
    t.string "administrator", limit: 30
    t.string "verified_by", limit: 30
  end

  create_table "ymrs_raw", force: :cascade do |t|
    t.bigint "subject_id"
    t.date "date"
    t.bigint "visit_num"
    t.bigint "study_id"
    t.integer "q1"
    t.integer "q2"
    t.bigint "q3"
    t.integer "q4"
    t.integer "q5"
    t.integer "q6"
    t.bigint "q7"
    t.bigint "q8"
    t.bigint "q9"
    t.bigint "q10"
    t.bigint "q11"
    t.string "administrator", limit: 20
    t.string "verified_by", limit: 20
  end

end
