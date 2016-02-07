<?xml version="1.0" encoding="UTF-8"?>
<mapping xsl:version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <model model="import_data.Question">
        <xsl:for-each select="//div[@class='question-summary narrow']">
            <item key="">
                <field name="title">
                    <xsl:value-of select=".//a[@class='question-hyperlink']"/>
                </field>
                <fk model="import_data.User">
                    <xsl:attribute name="key">
                        <xsl:value-of select="generate-id(.//div[@class='started']/a[2])"/>
                    </xsl:attribute>
                </fk>
                <xsl:for-each select=".//a[@class='post-tag']">
                    <m2mk model="import_data.Tag">
                        <xsl:attribute name="key">
                            <xsl:value-of select="generate-id(.)"/>
                        </xsl:attribute>
                    </m2mk>
                </xsl:for-each>
            </item>
        </xsl:for-each>
    </model>
    
    <model model="import_data.Tag">
        <xsl:for-each select="//a[@class='post-tag']">
            <item>
                <xsl:attribute name="key">
                    <xsl:value-of select="generate-id(.)"/>
                </xsl:attribute>
                <field name="title">
                    <xsl:value-of select="."/>
                </field>
            </item>
        </xsl:for-each>
    </model>
    
    <model model="import_data.User">
        <xsl:for-each select="//div[@class='started']/a[2]">
            <item>
                <xsl:attribute name="key">
                    <xsl:value-of select="generate-id(.)"/>
                </xsl:attribute>
                <field name="title">
                    <xsl:value-of select="."/>
                </field>
            </item>
        </xsl:for-each>
    </model>
</mapping>