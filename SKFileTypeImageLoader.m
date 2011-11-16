//
//  SKFileTypeImageLoader.m
//  SparkleShare
//
//  Created by Sergey Klimov on 16.11.11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import "SKFileTypeImageLoader.h"

@implementation SKFileTypeImageLoader
@synthesize config=_config;


static SKFileTypeImageLoader *sharedLoader = nil;

- (void)dealloc {
    [sharedLoader release];
    [_config release];
    [images release];
    [filenameFormat release];
    [super dealloc];
}

-(id) init {
    if (self=[super init]) {
        NSString *path = [[NSBundle mainBundle] pathForResource:
		                  @"FileTypeIcons" ofType: @"plist"];
		_config = [[NSDictionary alloc] initWithContentsOfFile: path];
        filenameFormat = [[_config objectForKey:@"Info"] objectForKey:@"FilenameFormat"];
        images = [[NSMutableDictionary alloc] init];
    }
    return self;
}

-(NSString*) constructFilenameWithBasename:(NSString*) basename size:(unsigned int) size {
    NSString *sizeString = [NSString stringWithFormat:@"%d", size];
    return  [[[filenameFormat 
                            stringByReplacingOccurrencesOfString:@"{size}" withString:sizeString] 
                           stringByReplacingOccurrencesOfString:@"{basename}" withString:basename] 
                          stringByReplacingOccurrencesOfString:@"{extension}" withString:@""];
}

-(UIImage*) loadImageWithName:(NSString*) imageName {
    if ([images objectForKey:imageName]) {
        return [images objectForKey:imageName];
    } else {
        NSString* path = [[NSBundle mainBundle] pathForResource:imageName ofType:@"png"];
        if (path) {
            UIImage* image = [UIImage imageWithContentsOfFile:path];
            [images setValue:image forKey:imageName];
            return image;
        } else {
            NSLog(@"WARNING! Image %@ not found", imageName);
            return nil;
        }
    }
}

-(UIImage *) imageForMimeType:(NSString *) mimeType size:(unsigned int) size {
    if (!mimeType) {
        return [self imageForMimeType:@"unknown" size:size];
    }
    
    NSString *basename = [mimeType stringByReplacingOccurrencesOfString:@"/" withString:@"-"];
    
    NSString* imageName = [self constructFilenameWithBasename:basename size:size];
    
    UIImage * image = [self loadImageWithName:imageName];
    if (image ==nil) {
        if ((basename=[[_config objectForKey:@"Synonyms"] objectForKey:basename])) {
            imageName = [self constructFilenameWithBasename:basename size:size];
            image = [self loadImageWithName:imageName];
        } else {
            NSLog(@"WARNING! Image %@ not found", imageName);
            return [self imageForMimeType:@"unknown" size:size];
        }
    }
    return image;
   
}

+ (SKFileTypeImageLoader *) sharedLoader {
    if (sharedLoader==nil)
        sharedLoader = [[SKFileTypeImageLoader alloc] init];
    return sharedLoader;
}

+(UIImage *) imageForMimeType:(NSString *) mimeType size:(unsigned int) size {
    return [[self sharedLoader] imageForMimeType:mimeType size:size];
}
@end
