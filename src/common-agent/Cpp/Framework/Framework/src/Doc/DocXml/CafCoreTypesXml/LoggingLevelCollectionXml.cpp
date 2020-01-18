/*
 *  Author: bwilliams
 *  Created: April 6, 2012
 *
 *  Copyright (C) 2012-2016 VMware, Inc.  All rights reserved. -- VMware Confidential
 *
 *  This code was generated by the script "build/dev/codeGen/genCppXml". Please
 *  speak to Brian W. before modifying it by hand.
 *
 */

#include "stdafx.h"

#include "Doc/CafCoreTypesDoc/CLoggingLevelCollectionDoc.h"
#include "Doc/CafCoreTypesDoc/CLoggingLevelElemDoc.h"
#include "Xml/XmlUtils/CXmlElement.h"
#include "Doc/DocXml/CafCoreTypesXml/LoggingLevelCollectionXml.h"
#include "Doc/DocXml/CafCoreTypesXml/LoggingLevelElemXml.h"

using namespace Caf;

void LoggingLevelCollectionXml::add(
	const SmartPtrCLoggingLevelCollectionDoc loggingLevelCollectionDoc,
	const SmartPtrCXmlElement thisXml) {
	CAF_CM_STATIC_FUNC_VALIDATE("LoggingLevelCollectionXml", "add");

	CAF_CM_ENTER {
		CAF_CM_VALIDATE_SMARTPTR(loggingLevelCollectionDoc);
		CAF_CM_VALIDATE_SMARTPTR(thisXml);

		const std::deque<SmartPtrCLoggingLevelElemDoc> loggingLevelVal =
			loggingLevelCollectionDoc->getLoggingLevel();
		CAF_CM_VALIDATE_STL(loggingLevelVal);

		if (! loggingLevelVal.empty()) {
			for (TConstIterator<std::deque<SmartPtrCLoggingLevelElemDoc> > loggingLevelIter(loggingLevelVal);
				loggingLevelIter; loggingLevelIter++) {
				const SmartPtrCXmlElement loggingLevelXml =
					thisXml->createAndAddElement("loggingLevel");
				LoggingLevelElemXml::add(*loggingLevelIter, loggingLevelXml);
			}
		}
	}
	CAF_CM_EXIT;
}

SmartPtrCLoggingLevelCollectionDoc LoggingLevelCollectionXml::parse(
	const SmartPtrCXmlElement thisXml) {
	CAF_CM_STATIC_FUNC_VALIDATE("LoggingLevelCollectionXml", "parse");

	SmartPtrCLoggingLevelCollectionDoc loggingLevelCollectionDoc;

	CAF_CM_ENTER {
		CAF_CM_VALIDATE_SMARTPTR(thisXml);

		const CXmlElement::SmartPtrCElementCollection loggingLevelChildrenXml =
			thisXml->findRequiredChildren("loggingLevel");

		std::deque<SmartPtrCLoggingLevelElemDoc> loggingLevelVal;
		if (! loggingLevelChildrenXml.IsNull() && ! loggingLevelChildrenXml->empty()) {
			for (TConstIterator<CXmlElement::CElementCollection> loggingLevelXmlIter(*loggingLevelChildrenXml);
				loggingLevelXmlIter; loggingLevelXmlIter++) {
				const SmartPtrCXmlElement loggingLevelXml = loggingLevelXmlIter->second;
				const SmartPtrCLoggingLevelElemDoc loggingLevelDoc =
					LoggingLevelElemXml::parse(loggingLevelXml);
				loggingLevelVal.push_back(loggingLevelDoc);
			}
		}

		loggingLevelCollectionDoc.CreateInstance();
		loggingLevelCollectionDoc->initialize(
			loggingLevelVal);
	}
	CAF_CM_EXIT;

	return loggingLevelCollectionDoc;
}

