<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- 
For more information, see: 
	http://blog.humaneguitarist.org/2011/11/12/pretty-printing-xml-with-python-lxml-and-xslt/

XSLT taken from Comment 4 by Michael Kay at: 
	http://www.dpawson.co.uk/xsl/sect2/pretty.html#d8621e19
-->
	<xsl:output method="xml" indent="yes" encoding="UTF-8"/>
	<xsl:strip-space elements="*"/>
	<xsl:template match="/">
		<xsl:copy-of select="."/>
	</xsl:template>
</xsl:stylesheet>