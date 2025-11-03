ActiveAdmin.register Miniscored do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :mde_current, :mde_recurrent, :mde_melancholic, :dysthymia, :suicidality, :suicidality_risk, :manic_current, :manic_past, :hypomanic_current, :hypomanic_past, :panic_disorder_current, :panic_disorder_lifetime, :agoraphobia, :social_phobia, :ocd, :ptsd, :alcohol_dependence, :alcohol_abuse, :substance_dependence, :dependence_substances_used, :substance_abuse, :abuse_substances_used, :psychotic_current, :psychotic_lifetime, :mood_current, :mood_lifetime, :anorexia, :bulimia, :anorexia_binge, :gad, :antisocial, :verified_by, :administrator
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :mde_current, :mde_recurrent, :mde_melancholic, :dysthymia, :suicidality, :suicidality_risk, :manic_current, :manic_past, :hypomanic_current, :hypomanic_past, :panic_disorder_current, :panic_disorder_lifetime, :agoraphobia, :social_phobia, :ocd, :ptsd, :alcohol_dependence, :alcohol_abuse, :substance_dependence, :dependence_substances_used, :substance_abuse, :abuse_substances_used, :psychotic_current, :psychotic_lifetime, :mood_current, :mood_lifetime, :anorexia, :bulimia, :anorexia_binge, :gad, :antisocial, :verified_by, :administrator]
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
      f.input :mde_current
      f.input :mde_recurrent
      f.input :mde_melancholic
      f.input :dysthymia
      f.input :suicidality
      f.input :suicidality_risk
      f.input :manic_current
      f.input :manic_past
      f.input :hypomanic_current
      f.input :hypomanic_past
      f.input :panic_disorder_current
      f.input :panic_disorder_lifetime
      f.input :agoraphobia
      f.input :social_phobia
      f.input :ocd
      f.input :ptsd
      f.input :alcohol_dependence
      f.input :alcohol_abuse
      f.input :substance_dependence
      f.input :dependence_substances_used
      f.input :substance_abuse
      f.input :abuse_substances_used
      f.input :psychotic_current
      f.input :psychotic_lifetime
      f.input :mood_current
      f.input :mood_lifetime
      f.input :anorexia
      f.input :bulimia
      f.input :anorexia_binge
      f.input :gad
      f.input :antisocial
      f.input :verified_by
      f.input :administrator
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



