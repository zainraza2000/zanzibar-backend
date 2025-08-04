revision = "0000000006"
down_revision = "0000000005"



def upgrade(migration):
    # write migration here
    migration.create_table(
        "todo",
        """
            "entity_id" varchar(32) NOT NULL,
            "version" varchar(32) NOT NULL,
            "previous_version" varchar(32) DEFAULT '00000000000000000000000000000000',
            "active" boolean DEFAULT true,
            "changed_by_id" varchar(32) DEFAULT NULL,
            "changed_on" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            "person_id" varchar(32) NOT NULL,
            "description" text NOT NULL,
            "status" varchar(32) DEFAULT 'pending',
            PRIMARY KEY ("entity_id")
        """
    )
    migration.add_index("todo", "todo_person_id_ind", "person_id")
    migration.add_index("todo", "todo_status_ind", "status")
    migration.add_index("todo", "todo_person_id_status_ind", "person_id, status")

    # Create the "todo_audit" table
    migration.create_table(
        "todo_audit",
        """
            "entity_id" varchar(32) NOT NULL,
            "version" varchar(32) NOT NULL,
            "previous_version" varchar(32) DEFAULT '00000000000000000000000000000000',
            "active" boolean DEFAULT true,
            "changed_by_id" varchar(32) DEFAULT NULL,
            "changed_on" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            "person_id" varchar(32) NOT NULL,
            "description" text NOT NULL,
            "status" varchar(32) DEFAULT 'pending',
            PRIMARY KEY ("entity_id", "version")
        """
    )

    migration.update_version_table(version=revision)


def downgrade(migration):
    # write migration here
    migration.drop_table(table_name="todo")
    migration.drop_table(table_name="todo_audit")

    migration.update_version_table(version=down_revision) 