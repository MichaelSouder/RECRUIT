# code to change the id of a table to primary key 
# and also make it serial
# this is for postgresql

=begin
  # how to change id to be a primary key
    # ALTER TABLE bicro_scored ADD PRIMARY KEY (id);
  # change int to serial
    # https://cornercase.info/change-existing-column-to-serial-in-postgres/
=end

def runsql(sql, run)
    # run sql or just print command if run=0
    if run == 1
        # run the sql
        ActiveRecord::Base.connection.execute(sql)
    end
    # print the sql
    puts sql
end

def alter_table(table_name, run=0)
=begin

1) Create the SEQUENCE that is used behind the scenes.

2) Assign the SEQUENCE to the COLUMN
alter table pc_product_contact alter column pc_uid set default nextval('pc_product_contact_uid_seq');

3) Find the value the SEQUENCE should start from
select max(pc_uid) from pc_product_contact --- this returns 7076 in my case

4) Inform the SEQUENCE to start from that value
ALTER SEQUENCE pc_product_contact_uid_seq
MINVALUE 7077   -- so start one higher than the max I got of 7076
START 7077
RESTART 7077;
=end

    # change the id to be a primary key
    sql = "ALTER TABLE #{table_name} ADD PRIMARY KEY (id);"
    #runsql(sql, run)

    # create sequence for the table
    newseq = "#{table_name}_id_seq"
    sql = "create sequence #{newseq};"
    #runsql(sql, run)

    # assign sequence 
    sql = "alter table #{table_name} alter column id set default nextval('#{newseq}');"
    #runsql(sql, run)

    # get the max value of id in tne table
    sql = "select max(id) from #{table_name};"
    maxid = ActiveRecord::Base.connection.execute(sql)[0]['max']
    newstart = maxid + 1
    # set the new starting value
    sql = "alter sequence #{newseq} start  #{newstart};"
    runsql(sql, run)
end


array = [Ahrs, Asrm, Auditc, Aware, Bai, Balanceboard, Bicro, Bis11, 
    Bicroscored, Bisbas, Dass21, Hit6, Mpai,Pssqi]
array.map do |item|
    puts "#{item} #{item.count}"
    puts "  uniq #{getuniq_id(item, allids)}"
end


# sample code for executing sql code
# records_array = ActiveRecord::Base.connection.execute(sql)
# lets get the maximum value from id of bicro_scored
sql = "select max(id) from bicro_scored ;"
maxid = ActiveRecord::Base.connection.execute(sql)[0]['max']
puts "Maxid in bicro_scored is #{maxid}"
