-- works table
copy works  (id,created, last_modified, revision,latest_revision,title,  subtitle, first_publish_date,description, number_of_editions)  from 'works.csv' with (FORCE_NULL(id,created, last_modified,revision,latest_revision,title,  subtitle, first_publish_date,description, number_of_editions), format csv, delimiter E'\t', QUOTE E'\b');

-- editions table
copy editions (id,created, last_modified, revision, latest_revision, title, subtitle, title_prefix, full_title, copyright_date, publish_date, by_statement,edition_name,volume_number, description,notes,number_of_pages,pagination,translation_of,dewey_decimal_class) from 'editions.csv' with (FORCE_NULL(id,created, last_modified,revision,latest_revision,title, subtitle,title_prefix,full_title,copyright_date,publish_date,publish_country,by_statement,edition_name,volume_number, description,notes,number_of_pages,pagination,translation_of,dewey_decimal_class), format csv, delimiter E'\t', QUOTE E'\b');

-- authors table
copy authors  (id,created, last_modified,revision,latest_revision,name,fuller_name,personal_name,birth_date,death_date,date,entity_type,bio)  from 'authors.csv' with (FORCE_NULL(id,created, last_modified,revision,latest_revision,name,fuller_name,personal_name,birth_date,death_date,date,entity_type,bio),format csv, delimiter E'\t', QUOTE E'\b');

-- works_authors table
copy works_authors (works_id,author_id) from 'works_authors.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');

-- works_covers table
copy works_covers (work_id,cover) from 'works_covers.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');

-- #works_dewey_numbers and dewey numbers tables
copy dewey_numbers (id, dewey_number) from 'dewey_number.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy works_dewey_number (work_id, dewey_number_id) from 'works_dewey_number_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');


-- works_lc_class, editions_lc_class, and lc_classifications tables
copy lc_classifications (id,lc_classification) from 'lc_classifications.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy works_lc_class (work_id,lc_classification_id) from 'works_lc_classifications_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_lc_class (edition_id,lc_classification_id) from 'editions_lc_classifications_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- works_original_languages, editions_languages, and langugage table
copy languages (id,language) from 'languages.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');
copy works_original_languages (work_id,language_id) from 'works_orginal_languages_id.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_languages (edition_id,language_id) from 'editions_languages_id.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');

-- works_other_titles and other_tiles tables
copy other_work_titles(id, other_title) from 'other_titles.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy works_other_titles (work_id,other_work_title_id) from 'works_other_titles_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- works_subjects, editions_subjects, and subjects tables
copy subjects (id,subject) from 'subjects.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy works_subjects (work_id,subject_id) from 'works_subjects_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_subjects (edition_id,subject_id) from 'editions_subjects_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- editions_authors table
copy editions_authors (edition_id,author_id) from 'editions_authors.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');

-- editions_contributors, contributors tables
copy contributors (id, contributor) from 'contributors.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_contributors (edition_id, contributor_id) from 'editions_contributors_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- editions_covers table
copy editions_covers (edition_id,cover) from 'editions_covers.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');

-- editions_genres, genres tables
copy genres (id, genre) from 'genres.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_genres (edition_id, genre_id) from 'editions_genres_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- editions_isbn_10 table
copy editions_isbn_10 (edition_id,isbn_10) from 'editions_isbn_10.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');

--editions_isbn_13 table
copy editions_isbn_13 (edition_id,isbn_13) from 'editions_isbn_13.csv'  with(format csv, delimiter E'\t', QUOTE E'\b');

-- editions_lccn, lccn tables
copy lccn (id, lccn) from 'lccn.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_lccn (edition_id, lccn_id) from 'editions_lccn_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- editions_publish_places, authors_locations, and places tables
copy places (id, place) from 'places.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_publish_places (edition_id, place_id) from 'editions_publish_places_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy authors_locations (author_id, location_id) from 'authors_location_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- authors_photos
copy photos (id, photo) from 'photos.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy authors_photos (author_id, photo_id) from 'authors_photos_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- publishers, editions_publishers tables
copy publishers (id, publisher) from 'publishers.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_publishers (edition_id, publisher_id) from 'editions_publishers_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- series, editions_series tables
copy series (id, series) from 'series.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_series (edition_id, series_id) from 'editions_series_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- work_titles, editions_work_titles tables
copy work_titles (id, work_title) from 'work_titles.csv' with(format csv, delimiter E'\t', QUOTE E'\b');
copy editions_work_titles (edition_id, work_title_id) from 'editions_work_titles_id.csv' with(format csv, delimiter E'\t', QUOTE E'\b');

-- editions_works
COPY editions_works (edition_id, work_id) FROM 'editions_works.csv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE E'\b');
