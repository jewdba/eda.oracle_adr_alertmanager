Oracle Automatic Diagnostic Repository alertmanager EDA source plugin
=====================================================================

Short Description
~~~~~~~~~~~~~~~~~
Receive events from Oracle Diagnostic Repository XML logfile based on a search pattern.

Description
~~~~~~~~~~~
- An ansible-rulebook event source module for getting events from Oracle Diagnostic Repository XML logfile.
- Regex-based pattern matching.

Options
-------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Option
     - Type
     - Description
   * - adr_home
     - String
     - **Required:** Oracle ADR home path.
   * - pattern
     - String
     - Optional: Regex used to match message text. Default: '(TNS|ORA)-[0-9]{5}'.
   * - delay
     - Integer
     - Optional: The number of seconds to wait between polling. Default: 1.


Examples
--------

.. code-block:: yaml

    - jewdba.eda.oracle_adr_alertmanager:
        adr_home: "/u01/app/oracle/diag/rdbms/mydb"
        pattern: 'ORA-[0-9]{5}'
        delay: 1

Author
------
jewdba

Requirements
------------
- Python >= 3.12
- ansible-core >=2.19
- ansible-rulebook >= 1.2

Version
-------
[version]