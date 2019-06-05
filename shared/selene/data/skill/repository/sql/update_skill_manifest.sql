UPDATE
    device.device_skill dev_skill
SET
    install_method = %(origin)s,
    install_status = %(installation)s,
    install_failure_reason = %(failure_message)s,
    install_ts = %(installed)s,
    update_ts = %(updated)s
WHERE
    id IN (
        SELECT
            dev_skill.id
        FROM
            device.device dev
        INNER JOIN
            device.device_skill dev_skill ON dev.id = dev_skill.device_id
        INNER JOIN
            skill.skill skill ON dev_skill.skill_id = skill.id
        LEFT JOIN
            skill.display skill_disp ON skill.id = skill_disp.skill_id
        WHERE
            dev.id = %(device_id)s AND (skill.family_name = %(name)s or skill_disp.display_data->>'name' = %(name)s)
    )