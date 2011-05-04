<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="/">

		<html xmlns="http://www.w3.org/1999/xhtml">
			<head>
				<title>OEE BDE File Processing Configurations</title>
				<style type="text/css">
					body {
					background-color: #BDCBDE;
					margin-left: 0px;
					margin-top: 0px;
					margin-right: 0px;
					margin-bottom: 0px;
					}
					.style1 {
					font-family: Arial,
					Helvetica, sans-serif;
					font-weight: bold;
					}
					.style2 {font-size: 24px}
					.style3 {color: #FFFFFF}
				</style>
			</head>

			<body>
				<table width="100%" border="0" cellpadding="0" cellspacing="0">
					<tr bgcolor="#003A7D">
						<td width="83%" valign="middle">
							<div align="left" class="style1 style2">
								<div align="center" class="style3">OEE BDE File Processing
									Configurations
								</div>
							</div>
						</td>
						<td width="17%" valign="middle">
							<img src="http://www.au.heidelberg.com/www/img/logo.gif" />
						</td>
					</tr>
				</table>
				<div>

					<xsl:for-each select="BdeSettings/Header/Client">
						<p>
							<b>Client: </b>
							<xsl:value-of select="Name" />
						</p>
					</xsl:for-each>
					<xsl:for-each select="BdeSettings/Header/Operator">
						<p>
							<b>Operator: </b>
							<xsl:value-of select="Name"></xsl:value-of>
						</p>
					</xsl:for-each>

					<table border="1">
						<caption><b>Sumup Configuration</b></caption>
						<tr color="#BDCBDE">
							<th>
								<font color="#003A7D">Name</font>
							</th>
							<th>
								<font color="#003A7D">Start Rule</font>
							</th>
							<th>
								<font color="#003A7D">Terminate Rule</font>
							</th>
							<th>
								<font color="#003A7D">End Rule</font>
							</th>
						</tr>
						<xsl:for-each select="BdeSettings/Sumups/Categories/Category">
							<tr>
								<th>
									<xsl:value-of select="@Name" />
								</th>
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
					<table border="1">
						<caption><b>Reporting Configuration</b></caption>
						<tr bgcolor="#BDCBDE">
							<th>
								<font color="#003A7D">Name</font>
							</th>
							<th>
								<font color="#003A7D">Rules</font>
							</th>
						</tr>
						<xsl:for-each select="BdeSettings/Reporting/Categories/Category">
							<tr>
								<th>
									<xsl:value-of select="@Name"></xsl:value-of>
								</th>
								<td>
									<xsl:for-each select="Rules/Rule">
										<xsl:value-of select="@Name" />
										<xsl:text>, </xsl:text>
									</xsl:for-each>
								</td>
							</tr>
						</xsl:for-each>
					</table>
				</div>
			</body>
		</html>
	</xsl:template>



</xsl:stylesheet>
