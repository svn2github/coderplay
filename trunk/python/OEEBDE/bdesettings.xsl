<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="/">

            <HTML xmlns="http://www.w3.org/1999/xhtml" >
            <head>
                <title>OEE BDE File Processing Configurations</title>
                <style type="text/css">
                    .style1
                    {
                        width: 100%;
                        background-color: #003A7D;
                    }
                    body {
                        margin-left: 0px;
                        margin-top: 0px;
                        margin-right: 0px;
                        margin-bottom: 0px;
                    }
                </style>
            </head>

			<BODY bgcolor="white">
				<table border="0" cellpadding="0" cellspacing="0" class="style1">
					<tr bgcolor="#003A7D">
						<td>
							<img
								src="http://www.au.heidelberg.com/www/img/560x13_hdm_area_top.gif" />
						</td>
						<td>
							<img src="http://www.au.heidelberg.com/www/img/logo.gif" />
						</td>
					</tr>
				</table>

					<h2>
						<font color="#003A7D">OEE BDE File Processing Configurations</font>
					</h2>
					<xsl:for-each select="BdeSettings/Header/Client">
						<P>
							<B>
								<xsl:text>Client: </xsl:text>
							</B>
							<xsl:value-of select="Name" />
						</P>
					</xsl:for-each>
					<xsl:for-each select="BdeSettings/Header/Operator">
						<P>
							<B>
								<xsl:text>Operator: </xsl:text>
							</B>
							<xsl:value-of select="Name"></xsl:value-of>
						</P>
					</xsl:for-each>

					<h4>Sumup Configuration</h4>
					<table border="1">
						<tr bgcolor="#BDCBDE">
							<th>Name</th>
							<th>Start Rule</th>
							<th>Terminate Rule</th>
							<th>End Rule</th>
						</tr>
						<xsl:for-each select="BdeSettings/Sumups/Categories/Category">
							<tr>
								<td>
									<xsl:value-of select="@Name" />
								</td>

								<td>
									<xsl:value-of select="StartRule/@Name" />
								</td>
								<td>
									<xsl:value-of select="TerminateRule/@Name" />
								</td>
								<td>
									<xsl:value-of select="EndRule/@Name" />
								</td>
							</tr>
						</xsl:for-each>

					</table>

					<br></br>
					<h4>Reporting Configuration</h4>
					<table border="1">
						<tr bgcolor="#BDCBDE">
							<th>Name</th>
							<th>Rules</th>
						</tr>
						<xsl:for-each select="BdeSettings/Reporting/Categories/Category">
							<tr>
								<td>
									<xsl:value-of select="@Name"></xsl:value-of>
								</td>
								<td>
									<xsl:for-each select="Rules/Rule">
										<xsl:value-of select="@Name" />
										<xsl:text>, </xsl:text>
									</xsl:for-each>
								</td>
							</tr>
						</xsl:for-each>
					</table>

			</BODY>
		</HTML>
	</xsl:template>



</xsl:stylesheet>
