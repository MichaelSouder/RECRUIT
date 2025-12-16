ActiveAdmin.register Mnbestconsensus do

    # See permitted parameters documentation:
    # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
    #
    # Uncomment all parameters which should be permitted for assignment
    #
    permit_params :subject_id, :date, :visit_num, :study_id, :blast_exposures, :blast_severity_1, :blast_severity_1_date, :blast_severity_2, :blast_severity_2_date, :blast_severity_3, :blast_severity_3_date, :nonblast_severity_total, :blast_severity_total, :blast_prob_def, :blast_poss_prob_def, :blast_unlikely_poss_prob_def, :blast_moderate_severe, :nonblast_exposures, :nonblast_severity_1, :nonblast_severity_1_date, :nonblast_severity_2, :nonblast_severity_2_date, :nonblast_severity_3, :nonblast_severity_3_date, :nonblast_severity_total, :nonblast_prob_def, :nonblast_poss_prob_def, :nonblast_unlikely_poss_prob_def, :nonblast_moderate_severe, :administrator, :initial_tbi_classification, :consensus_tbi_classification, :consensus_date, :consensus_group, :verified_by

   
    #
    # or
    #
    # permit_params do
    #   permitted = [:subject_id, :date, :visit_num, :study_id, :q1, :q2, :q3, :q4, :q5, :q6, :administrator, :verified_by]
    #   permitted << :other if params[:action] == 'create' && current_user.admin?
    #   permitted
    # end
    form do |f|
      f.semantic_errors
      f.inputs  do    
        f.input :date, :label => "Today's Date (yyyy-mm-dd)", as: :datepicker,
        datepicker_options: {
          min_date: "1900-01-01",
          max_date: "+3D"
        } 
        f.input :subject, :label => "Subject ID"
        f.input :study_id
        f.input :visit_num
        f.input :blast_exposures
        f.input :blast_severity_1
        f.input :blast_severity_1_date
        f.input :blast_severity_2
        f.input :blast_severity_2_date
        f.input :blast_severity_3
        f.input :blast_severity_3_date
        f.input :blast_severity_total
        f.input :blast_prob_def
        f.input :blast_unlikely_poss_prob_def
        f.input :blast_moderate_severe
        f.input :nonblast_exposures
        f.input :nonblast_severity_1
        f.input :nonblast_severity_1_date
        f.input :nonblast_severity_2
        f.input :nonblast_severity_2_date
        f.input :nonblast_severity_3
        f.input :nonblast_severity_3_date
        f.input :nonblast_severity_total
        f.input :nonblast_prob_def
        f.input :nonblast_poss_prob_def
        f.input :nonblast_unlikely_poss_prob_def
        f.input :nonblast_moderate_severe
        f.input :initial_tbi_classification
        f.input :consensus_tbi_classification
        f.input :consensus_date
        f.input :consensus_group
        f.input :administrator
        f.input :verified_by
      end
      f.actions         # adds the 'Submit' and 'Cancel' buttons
    end
    index do
      id_column
      column :subject
      column :date
      column :visit_num
      column :study_id
      column :administrator
      column :verified_by
      actions
    end 

    # specify filters
    # filter :id
    # filter :subject
    # filter :date
    # filter :visit_num
    # filter :administrator
    # filter :verified_by
    
  end
  